import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, Alert, Animated, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { MarineService } from '../services/marineService';
import { useAudioRecorder, RecordingPresets, requestRecordingPermissionsAsync } from 'expo-audio';

export default function AIScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const [inputText, setInputText] = useState('');
  
  // Status: idle | recording | processing
  const [status, setStatus] = useState<'idle' | 'recording' | 'processing'>('idle');
  const [responsePayload, setResponsePayload] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  
  // Visual pulsing indicator for recording
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    if (status === 'recording') {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.5, duration: 800, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 800, useNativeDriver: true })
        ])
      ).start();
    } else {
      pulseAnim.stopAnimation();
      pulseAnim.setValue(1);
    }
  }, [status]);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    setStatus('processing');
    setError(null);
    setResponsePayload(null);
    
    try {
      const res = await MarineService.sendChatIntent(undefined, inputText);
      setResponsePayload(res);
      setInputText('');
    } catch (err) {
      console.error("AI request failed:", err);
      setError(t('ai_error_fallback') || "Failed to connect to AI Service. Falling back to offline cache...");
    } finally {
      setStatus('idle');
    }
  };

  const startRecording = async () => {
    try {
      const permission = await requestRecordingPermissionsAsync();
      if (!permission.granted) {
        Alert.alert(t('permission_denied') || "Permission Denied", t('mic_access_required') || "Microphone access is required to use Voice AI.");
        return;
      }
      
      console.log("Preparing audio recorder...");
      await recorder.prepareToRecordAsync();

      console.log("Audio recording started...");
      recorder.record();
      setStatus('recording');
    } catch (err) {
      console.error('Failed to start recording:', err);
      Alert.alert("Error", "Failed to start recording");
      setStatus('idle');
    }
  };

  const stopRecording = async () => {
    if (status !== 'recording') return;
    
    try {
      console.log("Audio recording stopped...");
      await recorder.stop();
      
      const uri = recorder.uri;
      if (uri) {
        console.log("Valid audio file generated at URI:", uri);
        handleSendVoice(uri);
      } else {
        console.warn("No valid URI returned from recorder.");
        setStatus('idle');
      }
    } catch (err) {
      console.error('Failed to stop recording:', err);
      setStatus('idle');
    }
  };

  const handleSendVoice = async (uri: string) => {
    setStatus('processing');
    setError(null);
    setResponsePayload(null);
    try {
      const audioFile = {
        uri: uri,
        name: 'recording.m4a',
        type: 'audio/m4a',
      };
      console.log("Dispatching audio payload to backend...");
      const res = await MarineService.sendChatIntent(audioFile);
      setResponsePayload(res);
    } catch (err) {
      console.error("AI request failed:", err);
      setError("Failed to connect to AI Service. Falling back to offline cache...");
    } finally {
      setStatus('idle');
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
      <Text style={[typography.h2, { color: colors.textPrimary, padding: 16 }]}>
        {t('nav_ai') || 'ORCA AI Assistant'}
      </Text>
      
      <ScrollView style={styles.chatArea} contentContainerStyle={styles.chatContent}>
        {error && (
          <Text style={[typography.bodyMedium, { color: 'white', backgroundColor: 'red', padding: 10, marginBottom: 16, textAlign: 'center' }]}>
            {error}
          </Text>
        )}
        
        {responsePayload && responsePayload.text_response && (
          <View style={[styles.responseBox, { backgroundColor: colors.backgroundCard }]}>
            <Text style={[typography.bodyMedium, { color: colors.textPrimary }]}>
              {responsePayload.text_response}
            </Text>
          </View>
        )}
      </ScrollView>
      
      <View style={[styles.inputContainer, { borderTopColor: colors.surfaceBorder }]}>
        {status === 'recording' ? (
          <View style={styles.recordingOverlay}>
            <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
              <View style={styles.pulseCircle} />
            </Animated.View>
            <Text style={[typography.h3, { color: colors.accentBlue, marginLeft: 16 }]}>Listening...</Text>
            <View style={{ flex: 1 }} />
            <Button 
              title={t('stop') || "Stop"} 
              onPress={stopRecording} 
              variant="secondary" 
              style={{ backgroundColor: 'red', borderColor: 'red' }}
            />
          </View>
        ) : (
          <>
            <View style={styles.inputWrapper}>
              <Input 
                value={inputText}
                onChangeText={setInputText}
                placeholder={t('type_query') || "Type your query here..."}
                editable={status === 'idle'}
              />
            </View>
            
            {status === 'processing' ? (
              <ActivityIndicator size="large" color={colors.accentBlue} style={{ marginLeft: 16 }} />
            ) : (
              <View style={styles.actions}>
                <Button title={t('mic') || "Mic"} onPress={startRecording} variant="secondary" />
                <View style={{ width: 8 }} />
                <Button title={t('send') || "Send"} onPress={handleSend} variant="primary" disabled={status !== 'idle'} />
              </View>
            )}
          </>
        )}
      </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  chatArea: { flex: 1, paddingHorizontal: 16 },
  chatContent: { paddingVertical: 16 },
  responseBox: { padding: 16, borderRadius: 8, marginTop: 16 },
  inputContainer: { 
    flexDirection: 'row', 
    padding: 16, 
    borderTopWidth: 1, 
    alignItems: 'center' 
  },
  inputWrapper: { flex: 1 },
  actions: { flexDirection: 'row', marginLeft: 12, alignItems: 'center' },
  recordingOverlay: { flex: 1, flexDirection: 'row', alignItems: 'center' },
  pulseCircle: { width: 16, height: 16, borderRadius: 8, backgroundColor: 'red' }
});

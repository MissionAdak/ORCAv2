import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, Alert, Animated, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { MarineService } from '../services/marineService';
import { ExpoSpeechRecognitionModule, useSpeechRecognitionEvent } from 'expo-speech-recognition';

const getLocaleCode = (lang: string) => {
  const map: Record<string, string> = {
    'en': 'en-IN',
    'mr': 'mr-IN',
    'hi': 'hi-IN',
    'gu': 'gu-IN',
    'ta': 'ta-IN',
    'bn': 'bn-IN',
    'or': 'or-IN',
    'ml': 'ml-IN',
    'te': 'te-IN',
    'kn': 'kn-IN',
  };
  return map[lang] || 'en-IN';
};

export default function AIScreen() {
  const { colors, typography } = useTheme();
  const { t, language } = useLanguage();
  const [inputText, setInputText] = useState('');
  
  // Status: idle | recording | processing
  const [status, setStatus] = useState<'idle' | 'recording' | 'processing'>('idle');
  const [responsePayload, setResponsePayload] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
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

  useSpeechRecognitionEvent('result', (event) => {
    if (event.results && event.results.length > 0) {
      setInputText(event.results[0].transcript);
    }
  });

  useSpeechRecognitionEvent('end', () => {
    setStatus('idle');
  });

  useSpeechRecognitionEvent('error', (event) => {
    console.error('Speech recognition error:', event.error);
    if (event.error !== 'no-match') {
      setError("Voice recognition error: " + event.message);
    }
    setStatus('idle');
  });

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    setStatus('processing');
    setError(null);
    setResponsePayload(null);
    
    try {
      const res = await MarineService.sendChatIntent(inputText, language);
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
      setError(null);
      setInputText('');
      const perm = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
      if (!perm.granted) {
        Alert.alert("Error", "Failed to start speech recognition. Please grant microphone permissions.");
        return;
      }
      ExpoSpeechRecognitionModule.start({
        lang: getLocaleCode(language),
        interimResults: true,
        continuous: false,
      });
      setStatus('recording');
    } catch (err) {
      console.error('Failed to start recording:', err);
      Alert.alert("Error", "Failed to start speech recognition.");
      setStatus('idle');
    }
  };

  const stopRecording = () => {
    if (status !== 'recording') return;
    
    try {
      ExpoSpeechRecognitionModule.stop();
      setStatus('idle');
      // If we have text transcribed, send it
      if (inputText.trim()) {
        handleSend();
      }
    } catch (err) {
      console.error('Failed to stop recording:', err);
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

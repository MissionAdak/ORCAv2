import React, { useState } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { MarineService } from '../services/marineService';
import { Audio } from 'expo-av';

export default function AIScreen() {
  const { colors, typography } = useTheme();
  const { t } = useLanguage();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responsePayload, setResponsePayload] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setResponsePayload(null);
    
    try {
      // Sending text (fallback for voice) to MarineService
      const res = await MarineService.sendChatIntent(undefined, inputText);
      setResponsePayload(res);
      setInputText('');
    } catch (err) {
      console.error("AI request failed:", err);
      setError("Failed to connect to AI Service. Falling back to offline cache...");
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert("Error", "Failed to start recording");
    }
  };

  const stopRecording = async () => {
    setRecording(null);
    setIsRecording(false);
    
    if (recording) {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });
      const uri = recording.getURI();
      
      if (uri) {
        handleSendVoice(uri);
      }
    }
  };

  const handleSendVoice = async (uri: string) => {
    setIsLoading(true);
    setError(null);
    setResponsePayload(null);
    try {
      const audioFile = {
        uri: uri,
        name: 'recording.m4a',
        type: 'audio/m4a',
      };
      const res = await MarineService.sendChatIntent(audioFile);
      setResponsePayload(res);
    } catch (err) {
      console.error("AI request failed:", err);
      setError("Failed to connect to AI Service. Falling back to offline cache...");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.backgroundDark }]}>
      <Text style={[typography.h2, { color: colors.textPrimary, padding: 16 }]}>
        {t('nav_ai') || 'Bhashini AI Assistant'}
      </Text>
      
      <ScrollView style={styles.chatArea} contentContainerStyle={styles.chatContent}>
        {error && (
          <Text style={[typography.bodyMedium, { color: 'white', backgroundColor: 'red', padding: 10, marginBottom: 16, textAlign: 'center' }]}>
            {error}
          </Text>
        )}
        
        {responsePayload && (
          <View style={[styles.responseBox, { backgroundColor: colors.backgroundCard }]}>
            <Text style={[typography.bodyMedium, { color: colors.textPrimary, marginBottom: 8 }]}>
              AI Response Payload:
            </Text>
            <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
              {JSON.stringify(responsePayload, null, 2)}
            </Text>
          </View>
        )}
      </ScrollView>
      
      <View style={[styles.inputContainer, { borderTopColor: colors.surfaceBorder }]}>
        <View style={styles.inputWrapper}>
          <Input 
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your query here..."
          />
        </View>
        
        {isLoading ? (
          <ActivityIndicator size="large" color={colors.accentBlue} style={{ marginLeft: 16 }} />
        ) : (
          <View style={styles.actions}>
            <Button title={isRecording ? "Stop" : "Mic"} onPress={isRecording ? stopRecording : startRecording} variant="secondary" />
            <View style={{ width: 8 }} />
            <Button title="Send" onPress={handleSend} variant="primary" />
          </View>
        )}
      </View>
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
  actions: { flexDirection: 'row', marginLeft: 12, alignItems: 'center' }
});

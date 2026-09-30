import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { Card, Button } from '../components';

export default function ProfileScreen() {
  const { colors, typography, spacing, isWetHandMode, toggleWetHandMode } = useTheme();
  const { t, language, setLanguage, supportedLanguages } = useLanguage();
  const { user, logout } = useAuth();
  
  const [isEditing, setIsEditing] = useState(false);

  const handleLogout = async () => {
    Alert.alert(
      "Sign Out",
      "Are you sure you want to log out of ORCA?",
      [
        { text: "Cancel", style: "cancel" },
        { 
          text: "Logout", 
          style: "destructive",
          onPress: async () => {
            await logout();
            // Auth flow navigation is typically handled automatically by the Root Navigator observing Auth state
          }
        }
      ]
    );
  };

  const activeLanguageName = supportedLanguages.find(l => l.code === language)?.nativeLabel || 'English';

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.backgroundDark }]}>
      <ScrollView contentContainerStyle={[styles.container, { padding: spacing.md }]}>
        
        <View style={styles.headerRow}>
          <Text style={[typography.h2, { color: colors.textPrimary }]}>
            {t('nav_profile')}
          </Text>
          <Button 
            title={isEditing ? "Save" : "Edit"} 
            onPress={() => setIsEditing(!isEditing)} 
            variant="outline" 
            style={styles.editBtn} 
          />
        </View>

        {/* Profile Identity Card */}
        <Card elevated>
          <View style={styles.profileHeader}>
            <View style={[styles.avatar, { backgroundColor: colors.accentBlue }]}>
              <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>
                {user?.name?.charAt(0)?.toUpperCase() || 'G'}
              </Text>
            </View>
            <View style={styles.profileInfo}>
              <Text style={[typography.h3, { color: colors.textPrimary }]}>
                {user?.name || 'Guest Fisher / Offline Demo Mode'}
              </Text>
              <Text style={[typography.bodyMedium, { color: colors.textMuted }]}>
                {user?.phone || 'No phone number linked'}
              </Text>
              {user?.email && (
                <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
                  {user.email}
                </Text>
              )}
            </View>
          </View>
        </Card>

        {/* Vessel & Emergency Details */}
        <Card title="Vessel & Emergency" icon={<Ionicons name="boat-outline" size={20} color={colors.accentTeal} />}>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>Vessel Name:</Text>
            <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>{user?.vesselName || 'N/A'}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>Registration ID:</Text>
            <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>{user?.vesselId || 'N/A'}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>Emergency:</Text>
            <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>
              {user?.emergencyContacts?.join(', ') || 'None set'}
            </Text>
          </View>
        </Card>

        {/* Settings */}
        <Text style={[typography.h3, { color: colors.textPrimary, marginTop: spacing.md, marginBottom: spacing.sm }]}>
          Settings
        </Text>

        <Card title="Language / भाषा" icon={<Ionicons name="language-outline" size={20} color={colors.accentBlue} />}>
          <Text style={[typography.bodySmall, { color: colors.textMuted, marginBottom: 12 }]}>
            Active Language: {activeLanguageName}
          </Text>
          <View style={styles.langGrid}>
            {supportedLanguages.map((item) => (
              <Button
                key={item.code}
                title={`${item.nativeLabel} (${item.label})`}
                onPress={() => setLanguage(item.code)}
                variant={language === item.code ? 'primary' : 'secondary'}
                style={styles.langButton}
              />
            ))}
          </View>
        </Card>

        <Card title={t('wet_hand_mode')} subtitle="Enlarges tap targets and forces high-contrast" icon={<Ionicons name="hand-right-outline" size={20} color={colors.accentGold} />}>
          <Button
            title={isWetHandMode ? 'Enabled (64dp Target Active)' : 'Disabled (Standard 48dp)'}
            onPress={toggleWetHandMode}
            variant={isWetHandMode ? 'primary' : 'outline'}
          />
        </Card>

        {/* Logout Action */}
        <Button 
          title="Sign Out" 
          onPress={handleLogout} 
          variant="secondary" 
          style={{ marginTop: spacing.lg, borderColor: 'red', borderWidth: 1 }} 
        />
        
        <Text style={[typography.bodySmall, { color: colors.textMuted, textAlign: 'center', marginTop: 24 }]}>
          ORCA Maritime Decision-Support Platform · v2.0.0
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  container: { paddingBottom: 40 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  editBtn: { paddingVertical: 6, paddingHorizontal: 12, minWidth: 80 },
  profileHeader: { flexDirection: 'row', alignItems: 'center', padding: 8 },
  avatar: { width: 60, height: 60, borderRadius: 30, justifyContent: 'center', alignItems: 'center', marginRight: 16 },
  profileInfo: { flex: 1 },
  detailRow: { flexDirection: 'row', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#222' },
  langGrid: { gap: 8 },
  langButton: { width: '100%' },
});

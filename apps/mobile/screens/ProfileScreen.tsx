import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Input } from '../components';

export default function ProfileScreen() {
  const { colors, typography, spacing, isWetHandMode, toggleWetHandMode } = useTheme();
  const { t, language, setLanguage, supportedLanguages } = useLanguage();
  const { user, logout, updateProfile } = useAuth();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(user?.name || '');
  const [editHarbor, setEditHarbor] = useState(user?.harbor || '');
  const [editVesselName, setEditVesselName] = useState(user?.vesselName || '');
  const [editVesselId, setEditVesselId] = useState(user?.vesselId || '');
  const [editEmergencyContacts, setEditEmergencyContacts] = useState(user?.emergencyContacts?.join(', ') || '');

  const handleSave = async () => {
    await updateProfile({
      name: editName,
      harbor: editHarbor,
      vesselName: editVesselName,
      vesselId: editVesselId,
      emergencyContacts: editEmergencyContacts.split(',').map(s => s.trim()).filter(Boolean),
    });
    setIsEditing(false);
  };

  const handleLogout = async () => {
    Alert.alert(
      t('sign_out') || "Sign Out",
      t('sign_out_confirm') || "Are you sure you want to log out of ORCA?",
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
            title={isEditing ? t('profile_save') || "Save" : t('profile_edit') || "Edit"} 
            onPress={() => isEditing ? handleSave() : setIsEditing(true)} 
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
              {isEditing ? (
                <>
                  <Input value={editName} onChangeText={setEditName} placeholder={t('profile_name') || "Name"} />
                  <Input value={editHarbor} onChangeText={setEditHarbor} placeholder={t('profile_location') || "Location (e.g. Versova)"} style={{ marginTop: 8 }} />
                </>
              ) : (
                <>
                  <Text style={[typography.h3, { color: colors.textPrimary }]}>
                    {user?.name || t('guest_fisher') || 'Guest Fisher / Offline Demo Mode'}
                  </Text>
                  <Text style={[typography.bodyMedium, { color: colors.accentBlue, marginTop: 4 }]}>
                    <Ionicons name="location-outline" size={14} /> {user?.harbor || t('location_not_set') || 'Location not set'}
                  </Text>
                </>
              )}
              <Text style={[typography.bodyMedium, { color: colors.textMuted, marginTop: 4 }]}>
                {user?.phone || t('no_phone') || 'No phone number linked'}
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
        <Card title={t('vessel_emergency') || "Vessel & Emergency"} icon={<Ionicons name="boat-outline" size={20} color={colors.accentTeal} />}>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>{t('vessel_name') || "Vessel Name:"}</Text>
            {isEditing ? (
              <Input value={editVesselName} onChangeText={setEditVesselName} style={{ flex: 1 }} />
            ) : (
              <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>{user?.vesselName || t('vessel_na') || 'N/A'}</Text>
            )}
          </View>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>{t('registration_id') || "Registration ID:"}</Text>
            {isEditing ? (
              <Input value={editVesselId} onChangeText={setEditVesselId} style={{ flex: 1 }} />
            ) : (
              <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>{user?.vesselId || t('vessel_na') || 'N/A'}</Text>
            )}
          </View>
          <View style={styles.detailRow}>
            <Text style={[typography.bodyMedium, { color: colors.textMuted, width: 120 }]}>{t('emergency_contact') || "Emergency:"}</Text>
            {isEditing ? (
              <Input value={editEmergencyContacts} onChangeText={setEditEmergencyContacts} style={{ flex: 1 }} placeholder={t('comma_separated') || "Comma separated"} />
            ) : (
              <Text style={[typography.bodyMedium, { color: colors.textPrimary, flex: 1 }]}>
                {user?.emergencyContacts?.join(', ') || t('none_set') || 'None set'}
              </Text>
            )}
          </View>
        </Card>

        {/* Settings */}
        <Text style={[typography.h3, { color: colors.textPrimary, marginTop: spacing.md, marginBottom: spacing.sm }]}>
          {t('settings') || 'Settings'}
        </Text>

        <Card title="Language / भाषा" icon={<Ionicons name="language-outline" size={20} color={colors.accentBlue} />}>
          <Text style={[typography.bodySmall, { color: colors.textMuted, marginBottom: 12 }]}>
            {t('active_language') || 'Active Language:'} {activeLanguageName}
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

        <Card title={t('wet_hand_mode')} subtitle={t('wet_hand_desc') || "Enlarges tap targets and forces high-contrast"} icon={<Ionicons name="hand-right-outline" size={20} color={colors.accentGold} />}>
          <Button
            title={isWetHandMode ? (t('enabled_64dp') || 'Enabled (64dp Target Active)') : (t('disabled_48dp') || 'Disabled (Standard 48dp)')}
            onPress={toggleWetHandMode}
            variant={isWetHandMode ? 'primary' : 'outline'}
          />
        </Card>

        {/* Logout Action */}
        <Button 
          title={t('sign_out') || "Sign Out"} 
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

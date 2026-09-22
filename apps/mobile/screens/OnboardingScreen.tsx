import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useUser, COMMON_HARBORS, VesselProfile } from '../context/UserContext';
import { Button, Card, Input, Stepper, Modal } from '../components';
import { RootStackScreenProps } from '../navigation/types';

export default function OnboardingScreen({ navigation }: RootStackScreenProps<'Onboarding'>) {
  const { colors, typography, spacing, isWetHandMode, triggerHaptic } = useTheme();
  const { language, setLanguage, supportedLanguages, t } = useLanguage();
  const {
    fisher,
    vessel,
    emergencyContacts,
    hasLocationPermission,
    selectedHarbor,
    updateFisherProfile,
    updateVesselProfile,
    addEmergencyContact,
    removeEmergencyContact,
    setLocationPermission,
    setSelectedHarbor,
    completeOnboarding,
  } = useUser();

  const [currentStep, setCurrentStep] = useState<number>(1);

  // Form states
  const [fisherName, setFisherName] = useState(fisher.name);
  const [fisherPhone, setFisherPhone] = useState(fisher.phone);
  const [vesselId, setVesselId] = useState(vessel.vesselId);
  const [vesselName, setVesselName] = useState(vessel.vesselName);
  const [vesselType, setVesselType] = useState<VesselProfile['vesselType']>(vessel.vesselType);
  const [crewCount, setCrewCount] = useState(String(vessel.crewCount || 4));

  // Emergency contact temp inputs
  const [contactName, setContactName] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [contactRelation, setContactRelation] = useState('Family');

  // Skip contacts warning modal
  const [isSkipModalVisible, setIsSkipModalVisible] = useState(false);

  const stepTitles = [
    'Language / भाषा',
    'Location Permission',
    'Fisher Profile',
    'Vessel Specifications',
    'Emergency Contacts',
  ];

  const handleNext = async () => {
    triggerHaptic('light');

    if (currentStep === 1) {
      setCurrentStep(2);
    } else if (currentStep === 2) {
      setCurrentStep(3);
    } else if (currentStep === 3) {
      if (!fisherName.trim() || !fisherPhone.trim()) {
        Alert.alert('Required Fields', 'Please enter your name and phone number.');
        return;
      }
      await updateFisherProfile({
        name: fisherName,
        phone: fisherPhone,
      });
      setCurrentStep(4);
    } else if (currentStep === 4) {
      if (!vesselId.trim()) {
        Alert.alert('Required Field', 'Please enter your vessel registration number.');
        return;
      }
      await updateVesselProfile({
        vesselId: vesselId.trim().toUpperCase(),
        vesselName: vesselName.trim(),
        vesselType,
        crewCount: parseInt(crewCount, 10) || 4,
      });
      setCurrentStep(5);
    } else if (currentStep === 5) {
      if (emergencyContacts.length === 0) {
        setIsSkipModalVisible(true);
        return;
      }
      await finishOnboarding();
    }
  };

  const handleBack = () => {
    triggerHaptic('light');
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const finishOnboarding = async () => {
    await completeOnboarding();
    triggerHaptic('success');
    navigation.replace('Auth');
  };

  const handleAddContact = async () => {
    if (!contactName.trim() || !contactPhone.trim()) {
      Alert.alert('Incomplete Contact', 'Please provide both contact name and phone number.');
      return;
    }
    await addEmergencyContact({
      name: contactName.trim(),
      phone: contactPhone.trim(),
      relation: contactRelation,
    });
    setContactName('');
    setContactPhone('');
    triggerHaptic('light');
  };

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.backgroundDark }]}>
      <View style={{ paddingHorizontal: spacing.md, paddingTop: spacing.xs }}>
        <Stepper
          currentStep={currentStep}
          totalSteps={5}
          stepTitles={stepTitles}
        />
      </View>

      <ScrollView
        contentContainerStyle={[styles.contentContainer, { padding: spacing.md }]}
        showsVerticalScrollIndicator={false}
      >
        {/* ================= STEP 1: LANGUAGE ================= */}
        {currentStep === 1 && (
          <View>
            <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginBottom: 16 }]}>
              Select your preferred language. All voice prompts, marine advisories, and risk briefings will be delivered in this language.
            </Text>

            {supportedLanguages.map((lang) => {
              const isSelected = language === lang.code;
              return (
                <TouchableOpacity
                  key={lang.code}
                  activeOpacity={0.8}
                  onPress={() => {
                    setLanguage(lang.code);
                    triggerHaptic('medium');
                  }}
                  style={[
                    styles.langCard,
                    {
                      backgroundColor: isSelected ? colors.backgroundCardElevated : colors.backgroundCard,
                      borderColor: isSelected ? colors.accentGold : colors.surfaceBorder,
                      minHeight: isWetHandMode ? spacing.touchTargetWetHand : 56,
                      borderRadius: spacing.radiusMd,
                      paddingHorizontal: spacing.md,
                      marginBottom: spacing.sm,
                    },
                  ]}
                >
                  <View style={styles.langLeft}>
                    <Ionicons
                      name="radio-button-on"
                      size={22}
                      color={isSelected ? colors.accentGold : colors.surfaceBorderActive}
                    />
                    <Text
                      style={[
                        typography.h3,
                        {
                          color: isSelected ? colors.accentGold : colors.textPrimary,
                          marginLeft: 12,
                        },
                      ]}
                    >
                      {lang.nativeLabel}
                    </Text>
                  </View>
                  <Text style={[typography.bodySmall, { color: colors.textSecondary }]}>
                    {lang.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        )}

        {/* ================= STEP 2: LOCATION ================= */}
        {currentStep === 2 && (
          <View>
            <Card elevated style={{ marginBottom: spacing.md, borderColor: colors.accentBlue }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
                <Ionicons name="navigate-circle" size={28} color={colors.accentBlue} style={{ marginRight: 8 }} />
                <Text style={[typography.h3, { color: colors.textPrimary }]}>GPS Geofencing & Safety</Text>
              </View>
              <Text style={[typography.bodyMedium, { color: colors.textSecondary }]}>
                ORCA requires location access to monitor proximity to the International Maritime Boundary Line (IMBL), warn against marine protected areas, and pinpoint distress coordinates.
              </Text>
              <View style={{ marginTop: 14 }}>
                <Button
                  title={hasLocationPermission ? '✓ GPS Access Granted' : 'Grant GPS Location Access'}
                  onPress={() => {
                    setLocationPermission(true);
                    triggerHaptic('success');
                  }}
                  variant={hasLocationPermission ? 'secondary' : 'primary'}
                  icon={<Ionicons name="locate" size={20} color={hasLocationPermission ? colors.riskLow : colors.textInverted} />}
                />
              </View>
            </Card>

            <Text style={[typography.label, { color: colors.textSecondary, marginBottom: 8 }]}>
              Or Select Your Primary Home Harbor:
            </Text>

            <View style={styles.harborList}>
              {COMMON_HARBORS.map((harbor) => {
                const isSelected = selectedHarbor.name === harbor.name;
                return (
                  <TouchableOpacity
                    key={harbor.name}
                    onPress={() => {
                      setSelectedHarbor(harbor);
                      triggerHaptic('light');
                    }}
                    style={[
                      styles.harborItem,
                      {
                        backgroundColor: isSelected ? 'rgba(0, 168, 232, 0.2)' : colors.backgroundCard,
                        borderColor: isSelected ? colors.accentBlue : colors.surfaceBorder,
                        borderRadius: spacing.radiusSm,
                        padding: spacing.sm,
                        marginBottom: 6,
                      },
                    ]}
                  >
                    <View>
                      <Text style={[typography.button, { color: isSelected ? colors.accentBlue : colors.textPrimary }]}>
                        {harbor.name}
                      </Text>
                      <Text style={[typography.bodySmall, { color: colors.textMuted }]}>
                        {harbor.state} · {harbor.lat}°N, {harbor.lon}°E
                      </Text>
                    </View>
                    {isSelected && (
                      <Ionicons name="checkmark-circle" size={22} color={colors.accentBlue} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        )}

        {/* ================= STEP 3: FISHER PROFILE ================= */}
        {currentStep === 3 && (
          <View>
            <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginBottom: 16 }]}>
              Enter your personal identification details. This information is linked to distress transmissions and official responder briefs.
            </Text>

            <Input
              label="Full Name (नाव)"
              value={fisherName}
              onChangeText={setFisherName}
              placeholder="e.g. Ramesh Koli"
              icon="person-outline"
            />

            <Input
              label="Mobile Phone (मोबाईल नंबर)"
              value={fisherPhone}
              onChangeText={setFisherPhone}
              placeholder="10-digit mobile number"
              keyboardType="phone-pad"
              icon="call-outline"
            />

            <Input
              label="Home Village / Coastal Harbor"
              value={selectedHarbor.name + ', ' + selectedHarbor.state}
              editable={false}
              icon="boat-outline"
              helperText="Configured in Step 2: Location"
            />
          </View>
        )}

        {/* ================= STEP 4: VESSEL SPECIFICATIONS ================= */}
        {currentStep === 4 && (
          <View>
            <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginBottom: 16 }]}>
              Vessel specifications allow the deterministic drift engine to select the correct leeway aerodynamics and hydrodynamics during emergencies.
            </Text>

            <Input
              label="Vessel Registration ID (नौका क्रमांक)"
              value={vesselId}
              onChangeText={setVesselId}
              placeholder="e.g. MH01AB1234"
              icon="barcode-outline"
              autoCapitalize="characters"
              helperText="Hard cap: 10 chars for 2G Compressed SMS encoding"
            />

            <Input
              label="Vessel Name (नौकेचे नाव)"
              value={vesselName}
              onChangeText={setVesselName}
              placeholder="e.g. Mata Krupa"
              icon="boat-outline"
            />

            <Text style={[typography.label, { color: colors.textSecondary, marginBottom: 8 }]}>
              Vessel Propulsion / Class:
            </Text>

            <View style={{ marginBottom: 16 }}>
              {[
                { id: 'motorized_obm', label: 'Motorized Artisanal (OBM)', desc: 'Small craft with Outboard Motor (Ramesh persona)' },
                { id: 'mechanized_trawler', label: 'Mechanized Trawler', desc: 'Decked trawler for multi-day trips (Suresh persona)' },
                { id: 'non_mechanized', label: 'Non-Mechanized Traditional', desc: 'Canoe, kattumaram, or sail craft' },
              ].map((item) => {
                const isSelected = vesselType === item.id;
                return (
                  <TouchableOpacity
                    key={item.id}
                    onPress={() => {
                      setVesselType(item.id as VesselProfile['vesselType']);
                      triggerHaptic('light');
                    }}
                    style={[
                      styles.vesselTypeCard,
                      {
                        backgroundColor: isSelected ? colors.backgroundCardElevated : colors.backgroundCard,
                        borderColor: isSelected ? colors.accentGold : colors.surfaceBorder,
                        borderRadius: spacing.radiusMd,
                        padding: spacing.md,
                        marginBottom: 8,
                      },
                    ]}
                  >
                    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                      <Ionicons
                        name={isSelected ? 'radio-button-on' : 'radio-button-off'}
                        size={20}
                        color={isSelected ? colors.accentGold : colors.textMuted}
                        style={{ marginRight: 10 }}
                      />
                      <Text style={[typography.button, { color: isSelected ? colors.accentGold : colors.textPrimary }]}>
                        {item.label}
                      </Text>
                    </View>
                    <Text style={[typography.bodySmall, { color: colors.textSecondary, marginTop: 4, marginLeft: 30 }]}>
                      {item.desc}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            <Input
              label="Normal Crew Count On Board"
              value={crewCount}
              onChangeText={setCrewCount}
              placeholder="4"
              keyboardType="number-pad"
              icon="people-outline"
              helperText="Pre-filled on emergency SOS creation"
            />
          </View>
        )}

        {/* ================= STEP 5: EMERGENCY CONTACTS ================= */}
        {currentStep === 5 && (
          <View>
            <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginBottom: 16 }]}>
              Safety Prerequisite: When you raise an SOS, ORCA alerts your configured contacts and Coast Guard liaison with your drift-predicted search area.
            </Text>

            {/* List of current contacts */}
            {emergencyContacts.map((contact) => (
              <Card key={contact.id} style={{ marginBottom: 10 }}>
                <View style={styles.contactRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={[typography.h3, { color: colors.textPrimary }]}>{contact.name}</Text>
                    <Text style={[typography.bodyMedium, { color: colors.accentGold }]}>{contact.phone}</Text>
                    <Text style={[typography.bodySmall, { color: colors.textMuted }]}>Relation: {contact.relation}</Text>
                  </View>
                  <TouchableOpacity
                    onPress={() => removeEmergencyContact(contact.id)}
                    style={styles.deleteButton}
                    hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                  >
                    <Ionicons name="trash-outline" size={22} color={colors.riskHigh} />
                  </TouchableOpacity>
                </View>
              </Card>
            ))}

            {/* Add contact form */}
            <Card title="Add Emergency Contact" elevated style={{ marginTop: 8 }}>
              <Input
                label="Contact Name"
                value={contactName}
                onChangeText={setContactName}
                placeholder="Family / Boat Owner / Leader"
                icon="person-add-outline"
              />
              <Input
                label="Contact Phone"
                value={contactPhone}
                onChangeText={setContactPhone}
                placeholder="10-digit number"
                keyboardType="phone-pad"
                icon="call-outline"
              />
              <Button
                title="+ Add Contact"
                onPress={handleAddContact}
                variant="secondary"
              />
            </Card>
          </View>
        )}

        {/* Navigation Buttons */}
        <View style={styles.actionRow}>
          {currentStep > 1 ? (
            <Button
              title="Back"
              onPress={handleBack}
              variant="outline"
              style={{ flex: 1, marginRight: 8 }}
            />
          ) : null}

          <Button
            title={currentStep === 5 ? 'Complete Onboarding' : 'Continue'}
            onPress={handleNext}
            variant="primary"
            style={{ flex: 2 }}
          />
        </View>

        {currentStep === 5 && emergencyContacts.length === 0 && (
          <TouchableOpacity
            onPress={() => setIsSkipModalVisible(true)}
            style={{ marginTop: 14, alignItems: 'center', padding: 10 }}
          >
            <Text style={[typography.bodySmall, { color: colors.accentGold, textDecorationLine: 'underline' }]}>
              Skip for now, remind me later (PRD Escape Hatch)
            </Text>
          </TouchableOpacity>
        )}
      </ScrollView>

      {/* Skip Warning Modal */}
      <Modal
        visible={isSkipModalVisible}
        onClose={() => setIsSkipModalVisible(false)}
        title="Emergency Contacts Missing"
      >
        <Text style={[typography.bodyMedium, { color: colors.textPrimary, marginBottom: 12 }]}>
          Configuring emergency contacts is safety-critical. Without emergency contacts, SOS alerts can only broadcast over public distress and MRCC frequencies.
        </Text>
        <Text style={[typography.bodySmall, { color: colors.riskModerate, marginBottom: 20 }]}>
          You will see a persistent reminder on your Profile screen until you configure at least one contact.
        </Text>
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <Button
            title="Go Back & Add"
            onPress={() => setIsSkipModalVisible(false)}
            variant="outline"
            style={{ flex: 1 }}
          />
          <Button
            title="Skip Anyway"
            onPress={async () => {
              setIsSkipModalVisible(false);
              await finishOnboarding();
            }}
            variant="danger"
            style={{ flex: 1 }}
          />
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: 40,
  },
  langCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1.5,
  },
  langLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  harborList: {
    marginTop: 4,
    marginBottom: 16,
  },
  harborItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
  },
  vesselTypeCard: {
    borderWidth: 1.5,
  },
  contactRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deleteButton: {
    padding: 8,
  },
  actionRow: {
    flexDirection: 'row',
    marginTop: 24,
    alignItems: 'center',
  },
});

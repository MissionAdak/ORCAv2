import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { Button, Card, Input, ErrorState } from '../components';
import { RootStackScreenProps } from '../navigation/types';

type AuthMode = 'login' | 'signup' | 'forgot';

export default function AuthScreen({ navigation }: RootStackScreenProps<'Auth'>) {
  const { colors, typography, spacing } = useTheme();
  const { t } = useLanguage();
  const { login, signup, loginAsDemo, resetPassword } = useAuth();

  const [mode, setMode] = useState<AuthMode>('login');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupPhone, setSignupPhone] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [forgotIdentifier, setForgotIdentifier] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [identifierError, setIdentifierError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [nameError, setNameError] = useState('');
  const [phoneError, setPhoneError] = useState('');

  const clearErrors = () => {
    setErrorMsg('');
    setSuccessMsg('');
    setIdentifierError('');
    setPasswordError('');
    setNameError('');
    setPhoneError('');
  };

  const switchMode = (newMode: AuthMode) => {
    clearErrors();
    setMode(newMode);
  };

  // ─── LOGIN ────────────────────────────────────────────────────────────────
  const handleLogin = async () => {
    clearErrors();
    let valid = true;

    if (!identifier.trim()) {
      setIdentifierError('Phone number or email is required.');
      valid = false;
    }
    if (!password.trim()) {
      setPasswordError('Password is required.');
      valid = false;
    }
    if (!valid) return;

    setIsLoading(true);
    const result = await login(identifier.trim(), password);
    setIsLoading(false);

    if (result.success) {
      navigation.replace('Main', { screen: 'Home' });
    } else {
      setErrorMsg(result.error ?? 'Login failed. Please try again.');
    }
  };

  // ─── SIGNUP ───────────────────────────────────────────────────────────────
  const handleSignup = async () => {
    clearErrors();
    let valid = true;

    if (!signupName.trim()) {
      setNameError('Full name is required.');
      valid = false;
    }
    if (!signupPhone.trim() || signupPhone.replace(/\D/g, '').length < 10) {
      setPhoneError('Enter a valid 10-digit mobile number.');
      valid = false;
    }
    if (!valid) return;

    setIsLoading(true);
    const result = await signup(signupName.trim(), signupPhone.trim(), signupPassword);
    setIsLoading(false);

    if (result.success) {
      navigation.replace('Main', { screen: 'Home' });
    } else {
      setErrorMsg(result.error ?? 'Signup failed. Please try again.');
    }
  };

  // ─── FORGOT PASSWORD ──────────────────────────────────────────────────────
  const handleForgotPassword = async () => {
    clearErrors();
    if (!forgotIdentifier.trim()) {
      setIdentifierError('Please enter your registered phone number or email.');
      return;
    }

    setIsLoading(true);
    const result = await resetPassword(forgotIdentifier.trim());
    setIsLoading(false);
    setSuccessMsg(result.message);
  };

  // ─── DEMO PERSONAS ────────────────────────────────────────────────────────
  const handleDemoLogin = async (persona: 'ramesh' | 'suresh') => {
    clearErrors();
    setIsLoading(true);
    await loginAsDemo(persona);
    setIsLoading(false);
    navigation.replace('Main', { screen: 'Home' });
  };

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.backgroundDark }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.kvContainer}
      >
        <ScrollView
          contentContainerStyle={[styles.scrollContent, { padding: spacing.lg }]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* ── Header ── */}
          <View style={[styles.header, { marginBottom: spacing.lg }]}>
            <View style={[styles.logoCircle, { backgroundColor: colors.backgroundNavy, borderColor: colors.accentGold }]}>
              <Ionicons name="boat" size={36} color={colors.accentGold} />
            </View>
            <Text style={[typography.h1, { color: colors.accentGold, letterSpacing: 2, marginTop: spacing.sm }]}>
              ORCA
            </Text>
            <Text style={[typography.bodySmall, { color: colors.textSecondary, marginTop: 2, textAlign: 'center' }]}>
              Marine Intelligence & Decision-Support
            </Text>
          </View>

          {/* ── Mode Tabs ── */}
          <View style={[styles.modeTabs, { backgroundColor: colors.backgroundCard, borderRadius: spacing.radiusMd, marginBottom: spacing.lg }]}>
            {(['login', 'signup'] as AuthMode[]).map((m) => (
              <TouchableOpacity
                key={m}
                onPress={() => switchMode(m)}
                style={[
                  styles.modeTab,
                  {
                    backgroundColor: mode === m ? colors.accentGold : 'transparent',
                    borderRadius: spacing.radiusMd - 2,
                  },
                ]}
              >
                <Text
                  style={[
                    typography.button,
                    { color: mode === m ? colors.textInverted : colors.textMuted },
                  ]}
                >
                  {m === 'login' ? 'Login' : 'Sign Up'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* ── Global Error ── */}
          {errorMsg !== '' && (
            <View style={[styles.alertBox, { backgroundColor: 'rgba(230,57,70,0.15)', borderColor: colors.riskHigh, borderRadius: spacing.radiusSm, padding: spacing.md, marginBottom: spacing.md }]}>
              <Ionicons name="alert-circle-outline" size={16} color={colors.riskHigh} style={{ marginRight: 8 }} />
              <Text style={[typography.bodySmall, { color: colors.riskHigh, flex: 1 }]}>{errorMsg}</Text>
            </View>
          )}

          {/* ── Success ── */}
          {successMsg !== '' && (
            <View style={[styles.alertBox, { backgroundColor: 'rgba(42,157,143,0.15)', borderColor: colors.riskLow, borderRadius: spacing.radiusSm, padding: spacing.md, marginBottom: spacing.md }]}>
              <Ionicons name="checkmark-circle-outline" size={16} color={colors.riskLow} style={{ marginRight: 8 }} />
              <Text style={[typography.bodySmall, { color: colors.riskLow, flex: 1 }]}>{successMsg}</Text>
            </View>
          )}

          {/* ════════════════ LOGIN FORM ════════════════ */}
          {mode === 'login' && (
            <View>
              <Input
                label="Phone Number or Email"
                value={identifier}
                onChangeText={setIdentifier}
                placeholder="9820012345 or user@email.com"
                keyboardType="email-address"
                autoCapitalize="none"
                icon="person-outline"
                error={identifierError}
              />

              <Input
                label="Password"
                value={password}
                onChangeText={setPassword}
                placeholder="••••••••"
                secureTextEntry
                icon="lock-closed-outline"
                error={passwordError}
              />

              <TouchableOpacity
                onPress={() => switchMode('forgot')}
                style={[styles.forgotLink, { marginBottom: spacing.md }]}
              >
                <Text style={[typography.bodySmall, { color: colors.accentGold, textDecorationLine: 'underline' }]}>
                  Forgot password?
                </Text>
              </TouchableOpacity>

              <Button
                title={isLoading ? 'Signing in…' : 'Sign In'}
                onPress={handleLogin}
                variant="primary"
                loading={isLoading}
                icon={<Ionicons name="log-in-outline" size={20} color={colors.textInverted} />}
                style={{ marginBottom: spacing.md }}
              />

              {/* PRD Disclaimer per Amendment 8.2 */}
              <Text style={[typography.bodySmall, { color: colors.textMuted, textAlign: 'center', marginBottom: spacing.lg }]}>
                ORCA provides probabilistic marine decision-support and is not a certified
                safety-of-life system. Always follow official Coast Guard advisories.
              </Text>

              {/* Demo Personas */}
              <View style={[styles.dividerRow, { marginBottom: spacing.md }]}>
                <View style={[styles.dividerLine, { backgroundColor: colors.divider }]} />
                <Text style={[typography.bodySmall, { color: colors.textMuted, paddingHorizontal: 10 }]}>
                  Quick Demo Access
                </Text>
                <View style={[styles.dividerLine, { backgroundColor: colors.divider }]} />
              </View>

              <View style={styles.demoRow}>
                <Card style={{ flex: 1, marginRight: 6 }}>
                  <Text style={[typography.label, { color: colors.accentGold, marginBottom: 4 }]}>
                    Artisanal Fisher
                  </Text>
                  <Text style={[typography.bodySmall, { color: colors.textSecondary, marginBottom: 8 }]}>
                    Ramesh Koli · Versova
                  </Text>
                  <Button
                    title="Login as Ramesh"
                    onPress={() => handleDemoLogin('ramesh')}
                    variant="secondary"
                    loading={isLoading}
                    size="standard"
                  />
                </Card>

                <Card style={{ flex: 1, marginLeft: 6 }}>
                  <Text style={[typography.label, { color: colors.accentBlue, marginBottom: 4 }]}>
                    Trawler Captain
                  </Text>
                  <Text style={[typography.bodySmall, { color: colors.textSecondary, marginBottom: 8 }]}>
                    Suresh Patil · Sassoon Dock
                  </Text>
                  <Button
                    title="Login as Suresh"
                    onPress={() => handleDemoLogin('suresh')}
                    variant="secondary"
                    loading={isLoading}
                    size="standard"
                  />
                </Card>
              </View>
            </View>
          )}

          {/* ════════════════ SIGNUP FORM ════════════════ */}
          {mode === 'signup' && (
            <View>
              <Input
                label="Full Name (नाव)"
                value={signupName}
                onChangeText={setSignupName}
                placeholder="e.g. Ramesh Koli"
                icon="person-outline"
                error={nameError}
              />

              <Input
                label="Mobile Phone Number"
                value={signupPhone}
                onChangeText={setSignupPhone}
                placeholder="10-digit mobile number"
                keyboardType="phone-pad"
                icon="call-outline"
                error={phoneError}
                helperText="Used as your login identifier and for SOS broadcasts"
              />

              <Input
                label="Password (Optional)"
                value={signupPassword}
                onChangeText={setSignupPassword}
                placeholder="Leave blank for OTP-based login"
                secureTextEntry
                icon="lock-closed-outline"
              />

              {/* Maritime Disclaimer per Amendment 8.2 */}
              <View style={[styles.disclaimerBox, { backgroundColor: 'rgba(255,183,3,0.1)', borderColor: colors.riskModerate, borderRadius: spacing.radiusSm, padding: spacing.md, marginBottom: spacing.md }]}>
                <Ionicons name="information-circle-outline" size={18} color={colors.riskModerate} style={{ marginRight: 8, marginTop: 2 }} />
                <View style={{ flex: 1 }}>
                  <Text style={[typography.label, { color: colors.riskModerate, marginBottom: 4 }]}>
                    MARITIME DECISION-SUPPORT DISCLAIMER
                  </Text>
                  <Text style={[typography.bodySmall, { color: colors.textSecondary, lineHeight: 18 }]}>
                    ORCA provides probabilistic safety intelligence and is NOT a certified safety-of-life (SOLAS) system. SAR search zones are decision-support probability estimates, not guaranteed survivor locations. Always follow official Indian Coast Guard (ICG) and IMD advisories. By registering you acknowledge this.
                  </Text>
                </View>
              </View>

              <Button
                title={isLoading ? 'Creating account…' : 'Create Account'}
                onPress={handleSignup}
                variant="primary"
                loading={isLoading}
                icon={<Ionicons name="person-add-outline" size={20} color={colors.textInverted} />}
                style={{ marginBottom: spacing.md }}
              />

              <TouchableOpacity onPress={() => switchMode('login')} style={styles.forgotLink}>
                <Text style={[typography.bodySmall, { color: colors.accentGold }]}>
                  Already have an account?{' '}
                  <Text style={{ textDecorationLine: 'underline' }}>Sign In</Text>
                </Text>
              </TouchableOpacity>
            </View>
          )}

          {/* ════════════════ FORGOT PASSWORD ════════════════ */}
          {mode === 'forgot' && (
            <View>
              <View style={[styles.backRow, { marginBottom: spacing.md }]}>
                <TouchableOpacity
                  onPress={() => switchMode('login')}
                  style={{ flexDirection: 'row', alignItems: 'center' }}
                  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                >
                  <Ionicons name="arrow-back" size={20} color={colors.accentGold} style={{ marginRight: 6 }} />
                  <Text style={[typography.bodyMedium, { color: colors.accentGold }]}>Back to Login</Text>
                </TouchableOpacity>
              </View>

              <Text style={[typography.h3, { color: colors.textPrimary, marginBottom: 6 }]}>
                Reset Password
              </Text>
              <Text style={[typography.bodyMedium, { color: colors.textSecondary, marginBottom: spacing.lg }]}>
                Enter your registered phone number or email. We will send you a reset link or OTP.
              </Text>

              <Input
                label="Phone Number or Email"
                value={forgotIdentifier}
                onChangeText={setForgotIdentifier}
                placeholder="9820012345 or user@email.com"
                keyboardType="email-address"
                autoCapitalize="none"
                icon="mail-outline"
                error={identifierError}
              />

              <Button
                title={isLoading ? 'Sending…' : 'Send Reset Instructions'}
                onPress={handleForgotPassword}
                variant="primary"
                loading={isLoading}
                icon={<Ionicons name="send-outline" size={20} color={colors.textInverted} />}
                style={{ marginBottom: spacing.md }}
              />

              {successMsg !== '' && (
                <View style={[styles.alertBox, { backgroundColor: 'rgba(42,157,143,0.15)', borderColor: colors.riskLow, borderRadius: spacing.radiusSm, padding: spacing.md }]}>
                  <Ionicons name="checkmark-circle-outline" size={16} color={colors.riskLow} style={{ marginRight: 8 }} />
                  <Text style={[typography.bodySmall, { color: colors.riskLow, flex: 1 }]}>{successMsg}</Text>
                </View>
              )}
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  kvContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 60,
  },
  header: {
    alignItems: 'center',
  },
  logoCircle: {
    width: 78,
    height: 78,
    borderRadius: 39,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modeTabs: {
    flexDirection: 'row',
    padding: 4,
  },
  modeTab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
  },
  alertBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    borderWidth: 1,
  },
  disclaimerBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    borderWidth: 1,
  },
  forgotLink: {
    alignItems: 'flex-end',
    paddingVertical: 4,
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dividerLine: {
    flex: 1,
    height: 1,
  },
  demoRow: {
    flexDirection: 'row',
  },
  backRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});

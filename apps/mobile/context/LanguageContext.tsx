import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type SupportedLanguage = 'mr' | 'hi' | 'en' | 'gu' | 'ta';

export interface LanguageOption {
  code: SupportedLanguage;
  label: string;
  nativeLabel: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिंदी' },
  { code: 'en', label: 'English', nativeLabel: 'English' },
  { code: 'gu', label: 'Gujarati', nativeLabel: 'ગુજરાતી' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்' },
];

const TRANSLATIONS: Record<SupportedLanguage, Record<string, string>> = {
  mr: {
    app_title: 'ओर्का',
    nav_home: 'मुख्य',
    nav_map: 'नकाशा',
    nav_ai: 'ओर्का एआय',
    nav_alerts: 'सूचना',
    nav_profile: 'प्रोफाइल',
    risk_low: 'कमी धोका',
    risk_moderate: 'मध्यम धोका',
    risk_high: 'जास्त धोका',
    ask_orca: 'ओर्काला विचारा',
    emergency_sos: 'आणीबाणी (SOS)',
    ocean_conditions: 'समुद्राची स्थिती',
    fishing_intelligence: 'मासेमारी माहिती',
    cached_banner: 'कॅश केलेला डेटा — जुनी माहिती',
    offline_mode: 'ऑफलाइन मोड',
    confirm: 'नक्की करा',
    cancel: 'रद्द करा',
    retry: 'पुन्हा प्रयत्न करा',
    wet_hand_mode: 'ओले हात आणि सूर्यप्रकाश मोड',
  },
  hi: {
    app_title: 'ओर्का',
    nav_home: 'होम',
    nav_map: 'मानचित्र',
    nav_ai: 'ओर्का एआई',
    nav_alerts: 'चेतावनी',
    nav_profile: 'प्रोफ़ाइल',
    risk_low: 'कम जोखिम',
    risk_moderate: 'मध्यम जोखिम',
    risk_high: 'उच्च जोखिम',
    ask_orca: 'ओर्का से पूछें',
    emergency_sos: 'आपातकालीन (SOS)',
    ocean_conditions: 'समुद्र की स्थिति',
    fishing_intelligence: 'मत्स्य पालन बुद्धिमत्ता',
    cached_banner: 'कैश किया गया डेटा — पुराना डेटा',
    offline_mode: 'ऑफ़लाइन मोड',
    confirm: 'पुष्टि करें',
    cancel: 'रद्द करें',
    retry: 'पुनः प्रयास करें',
    wet_hand_mode: 'वेट-हैंड और धूप मोड',
  },
  en: {
    app_title: 'ORCA',
    nav_home: 'Home',
    nav_map: 'Map',
    nav_ai: 'Ask ORCA',
    nav_alerts: 'Alerts',
    nav_profile: 'Profile',
    risk_low: 'LOW RISK',
    risk_moderate: 'MODERATE RISK',
    risk_high: 'HIGH RISK',
    ask_orca: 'Ask ORCA',
    emergency_sos: 'EMERGENCY (SOS)',
    ocean_conditions: 'Ocean Conditions',
    fishing_intelligence: 'Fishing Intelligence',
    cached_banner: 'Cached Data — Stale',
    offline_mode: 'Offline Mode',
    confirm: 'Confirm',
    cancel: 'Cancel',
    retry: 'Retry',
    wet_hand_mode: 'Wet-Hand & Glare Mode',
  },
  gu: {
    app_title: 'ઓર્કા',
    nav_home: 'હોમ',
    nav_map: 'નકશો',
    nav_ai: 'ઓર્કા AI',
    nav_alerts: 'ચેતવણીઓ',
    nav_profile: 'પ્રોફાઇલ',
    risk_low: 'ઓછું જોખમ',
    risk_moderate: 'મધ્યમ જોખમ',
    risk_high: 'વધુ જોખમ',
    ask_orca: 'ઓર્કાને પૂછો',
    emergency_sos: 'કટોકટી (SOS)',
    ocean_conditions: 'દરિયાઈ પરિસ્થિતિ',
    fishing_intelligence: 'માછીમારી માહિતી',
    cached_banner: 'કેશ્ડ ડેટા',
    offline_mode: 'ઑફલાઇન મોડ',
    confirm: 'ખાતરી કરો',
    cancel: 'રદ કરો',
    retry: 'ફરી પ્રયાસ કરો',
    wet_hand_mode: 'વેટ-હેન્ડ મોડ',
  },
  ta: {
    app_title: 'ஆர்கா',
    nav_home: 'முகப்பு',
    nav_map: 'வரைபடம்',
    nav_ai: 'ஆர்கா AI',
    nav_alerts: 'எச்சரிக்கைகள்',
    nav_profile: 'சுயவிவரம்',
    risk_low: 'குறைந்த ஆபத்து',
    risk_moderate: 'மிதமான ஆபத்து',
    risk_high: 'அதிக ஆபத்து',
    ask_orca: 'ஆர்காவிடம் கேளுங்கள்',
    emergency_sos: 'அவசர நிலை (SOS)',
    ocean_conditions: 'கடல் நிலைமை',
    fishing_intelligence: 'மீன்பிடி தகவல்கள்',
    cached_banner: 'தற்காலிக சேமிப்புத் தரவு',
    offline_mode: 'ஆஃப்லைன் பயன்முறை',
    confirm: 'உறுதி செய்',
    cancel: 'ரத்து செய்',
    retry: 'மீண்டும் முயற்சி செய்',
    wet_hand_mode: 'ஈரமான கை பயன்முறை',
  },
};

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => Promise<void>;
  t: (key: string) => string;
  supportedLanguages: LanguageOption[];
}

const STORAGE_KEY_LANGUAGE = '@orca_user_language';

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>('mr'); // Default to Marathi for artisanal persona

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY_LANGUAGE)
      .then((saved) => {
        if (saved && (saved in TRANSLATIONS)) {
          setLanguageState(saved as SupportedLanguage);
        }
      })
      .catch((err) => {
        console.warn('Failed to load user language:', err);
      });
  }, []);

  const setLanguage = async (newLang: SupportedLanguage) => {
    setLanguageState(newLang);
    try {
      await AsyncStorage.setItem(STORAGE_KEY_LANGUAGE, newLang);
    } catch (err) {
      console.warn('Failed to save user language:', err);
    }
  };

  const t = (key: string): string => {
    const langDict = TRANSLATIONS[language] || TRANSLATIONS.en;
    return langDict[key] || TRANSLATIONS.en[key] || key;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        supportedLanguages: SUPPORTED_LANGUAGES,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

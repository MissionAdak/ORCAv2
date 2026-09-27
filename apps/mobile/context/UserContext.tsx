import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface FisherProfile {
  name: string;
  phone: string;
  homeHarbor: string;
  coastalState: string;
}

export interface VesselProfile {
  vesselId: string;
  vesselName: string;
  vesselType: 'non_mechanized' | 'motorized_obm' | 'mechanized_trawler';
  crewCount: number;
}

export interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relation: string;
}

export interface HomeHarborLocation {
  name: string;
  state: string;
  lat: number;
  lon: number;
}

export const COMMON_HARBORS: HomeHarborLocation[] = [
  { name: 'Versova', state: 'Maharashtra', lat: 19.13, lon: 72.81 },
  { name: 'Sassoon Dock', state: 'Maharashtra', lat: 18.91, lon: 72.82 },
  { name: 'Ratnagiri', state: 'Maharashtra', lat: 16.98, lon: 73.28 },
  { name: 'Porbandar', state: 'Gujarat', lat: 21.64, lon: 69.60 },
  { name: 'Veraval', state: 'Gujarat', lat: 20.90, lon: 70.36 },
  { name: 'Mangalore', state: 'Karnataka', lat: 12.87, lon: 74.84 },
  { name: 'Kochi (Cochin)', state: 'Kerala', lat: 9.96, lon: 76.24 },
  { name: 'Chennai', state: 'Tamil Nadu', lat: 13.08, lon: 80.29 },
  { name: 'Visakhapatnam', state: 'Andhra Pradesh', lat: 17.68, lon: 83.21 },
];

interface UserContextType {
  fisher: FisherProfile;
  vessel: VesselProfile;
  emergencyContacts: EmergencyContact[];
  isOnboarded: boolean;
  hasLocationPermission: boolean;
  selectedHarbor: HomeHarborLocation;
  updateFisherProfile: (profile: Partial<FisherProfile>) => Promise<void>;
  updateVesselProfile: (vessel: Partial<VesselProfile>) => Promise<void>;
  addEmergencyContact: (contact: Omit<EmergencyContact, 'id'>) => Promise<void>;
  removeEmergencyContact: (id: string) => Promise<void>;
  setLocationPermission: (granted: boolean) => Promise<void>;
  setSelectedHarbor: (harbor: HomeHarborLocation) => Promise<void>;
  completeOnboarding: () => Promise<void>;
  resetUserData: () => Promise<void>;
}

const STORAGE_KEYS = {
  FISHER: '@orca_fisher_profile',
  VESSEL: '@orca_vessel_profile',
  CONTACTS: '@orca_emergency_contacts',
  ONBOARDED: '@orca_is_onboarded',
  LOCATION_PERM: '@orca_location_permission',
  HARBOR: '@orca_selected_harbor',
};

const DEFAULT_FISHER: FisherProfile = {
  name: 'Ramesh Koli',
  phone: '9820012345',
  homeHarbor: 'Versova',
  coastalState: 'Maharashtra',
};

const DEFAULT_VESSEL: VesselProfile = {
  vesselId: 'MH01AB1234',
  vesselName: 'Mata Krupa',
  vesselType: 'motorized_obm',
  crewCount: 4,
};

const DEFAULT_CONTACTS: EmergencyContact[] = [
  {
    id: 'c-1',
    name: 'Suresh Patil',
    phone: '9820098765',
    relation: 'Cooperative Leader',
  },
];

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [fisher, setFisher] = useState<FisherProfile>(DEFAULT_FISHER);
  const [vessel, setVessel] = useState<VesselProfile>(DEFAULT_VESSEL);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>(DEFAULT_CONTACTS);
  const [isOnboarded, setIsOnboarded] = useState<boolean>(false);
  const [hasLocationPermission, setHasLocationPermission] = useState<boolean>(false);
  const [selectedHarbor, setSelectedHarborState] = useState<HomeHarborLocation>(COMMON_HARBORS[0]);

  useEffect(() => {
    const loadState = async () => {
      try {
        const [savedFisher, savedVessel, savedContacts, savedOnboarded, savedPerm, savedHarbor] =
          await Promise.all([
            AsyncStorage.getItem(STORAGE_KEYS.FISHER),
            AsyncStorage.getItem(STORAGE_KEYS.VESSEL),
            AsyncStorage.getItem(STORAGE_KEYS.CONTACTS),
            AsyncStorage.getItem(STORAGE_KEYS.ONBOARDED),
            AsyncStorage.getItem(STORAGE_KEYS.LOCATION_PERM),
            AsyncStorage.getItem(STORAGE_KEYS.HARBOR),
          ]);

        if (savedFisher) setFisher(JSON.parse(savedFisher));
        if (savedVessel) setVessel(JSON.parse(savedVessel));
        if (savedContacts) setEmergencyContacts(JSON.parse(savedContacts));
        if (savedOnboarded) setIsOnboarded(savedOnboarded === 'true');
        if (savedPerm) setHasLocationPermission(savedPerm === 'true');
        if (savedHarbor) setSelectedHarborState(JSON.parse(savedHarbor));
      } catch (err) {
        console.warn('Failed to load user state from storage:', err);
      }
    };

    loadState();
  }, []);

  const updateFisherProfile = async (partial: Partial<FisherProfile>) => {
    const updated = { ...fisher, ...partial };
    setFisher(updated);
    await AsyncStorage.setItem(STORAGE_KEYS.FISHER, JSON.stringify(updated));
  };

  const updateVesselProfile = async (partial: Partial<VesselProfile>) => {
    const updated = { ...vessel, ...partial };
    setVessel(updated);
    await AsyncStorage.setItem(STORAGE_KEYS.VESSEL, JSON.stringify(updated));
  };

  const addEmergencyContact = async (contact: Omit<EmergencyContact, 'id'>) => {
    const newContact: EmergencyContact = {
      ...contact,
      id: 'c-' + Date.now(),
    };
    const updated = [...emergencyContacts, newContact];
    setEmergencyContacts(updated);
    await AsyncStorage.setItem(STORAGE_KEYS.CONTACTS, JSON.stringify(updated));
  };

  const removeEmergencyContact = async (id: string) => {
    const updated = emergencyContacts.filter((c) => c.id !== id);
    setEmergencyContacts(updated);
    await AsyncStorage.setItem(STORAGE_KEYS.CONTACTS, JSON.stringify(updated));
  };

  const setLocationPermission = async (granted: boolean) => {
    setHasLocationPermission(granted);
    await AsyncStorage.setItem(STORAGE_KEYS.LOCATION_PERM, String(granted));
  };

  const setSelectedHarbor = async (harbor: HomeHarborLocation) => {
    setSelectedHarborState(harbor);
    await AsyncStorage.setItem(STORAGE_KEYS.HARBOR, JSON.stringify(harbor));
    await updateFisherProfile({ homeHarbor: harbor.name, coastalState: harbor.state });
  };

  const completeOnboarding = async () => {
    setIsOnboarded(true);
    await AsyncStorage.setItem(STORAGE_KEYS.ONBOARDED, 'true');
  };

  const resetUserData = async () => {
    await Promise.all([
      AsyncStorage.removeItem(STORAGE_KEYS.FISHER),
      AsyncStorage.removeItem(STORAGE_KEYS.VESSEL),
      AsyncStorage.removeItem(STORAGE_KEYS.CONTACTS),
      AsyncStorage.removeItem(STORAGE_KEYS.ONBOARDED),
      AsyncStorage.removeItem(STORAGE_KEYS.LOCATION_PERM),
      AsyncStorage.removeItem(STORAGE_KEYS.HARBOR),
    ]);
    setFisher(DEFAULT_FISHER);
    setVessel(DEFAULT_VESSEL);
    setEmergencyContacts(DEFAULT_CONTACTS);
    setIsOnboarded(false);
    setHasLocationPermission(false);
  };

  return (
    <UserContext.Provider
      value={{
        fisher,
        vessel,
        emergencyContacts,
        isOnboarded,
        hasLocationPermission,
        selectedHarbor,
        updateFisherProfile,
        updateVesselProfile,
        addEmergencyContact,
        removeEmergencyContact,
        setLocationPermission,
        setSelectedHarbor,
        completeOnboarding,
        resetUserData,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

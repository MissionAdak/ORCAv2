import type { BottomTabScreenProps as RNBottomTabScreenProps } from '@react-navigation/bottom-tabs';
import type { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

/**
 * Bottom Tab Navigation Parameters (Home | Map | AI | Alerts | Profile)
 */
export type BottomTabParamList = {
  Home: undefined;
  Map: undefined;
  AI: undefined;
  Alerts: undefined;
  Profile: undefined;
};

/**
 * Root Stack Navigation Parameters (Splash -> Onboarding -> Auth -> Main + SOS Modal)
 */
export type RootStackParamList = {
  Splash: undefined;
  Onboarding: undefined;
  Auth: undefined;
  Main: NavigatorScreenParams<BottomTabParamList>;
  EmergencySOSModal: undefined;
};

export type RootStackScreenProps<T extends keyof RootStackParamList> = NativeStackScreenProps<
  RootStackParamList,
  T
>;

export type BottomTabScreenProps<T extends keyof BottomTabParamList> = CompositeScreenProps<
  RNBottomTabScreenProps<BottomTabParamList, T>,
  NativeStackScreenProps<RootStackParamList>
>;

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}

import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface AuthUser {
  id: string;
  name: string;
  phone: string;
  email?: string;
  role: 'fisher' | 'captain' | 'dispatcher';
  harbor?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, password?: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, phone: string, password?: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  loginAsDemo: (persona: 'ramesh' | 'suresh') => Promise<void>;
  resetPassword: (identifier: string) => Promise<{ success: boolean; message: string }>;
}

const STORAGE_KEY_AUTH = '@orca_auth_user';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY_AUTH)
      .then((saved) => {
        if (saved) {
          try {
            setUser(JSON.parse(saved));
          } catch {
            setUser(null);
          }
        }
      })
      .catch((err) => {
        console.warn('Failed to read auth state:', err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const login = async (identifier: string, password?: string) => {
    setIsLoading(true);
    // Simulate lightweight auth check (Supabase Auth contract ready)
    await new Promise((resolve) => setTimeout(resolve, 600));

    if (!identifier.trim()) {
      setIsLoading(false);
      return { success: false, error: 'Please enter your phone number or email.' };
    }

    const newUser: AuthUser = {
      id: 'usr-' + Date.now(),
      name: identifier.includes('@') ? identifier.split('@')[0] : 'Coastal Fisher',
      phone: identifier.includes('@') ? '9876543210' : identifier,
      email: identifier.includes('@') ? identifier : undefined,
      role: 'fisher',
      harbor: 'Versova',
    };

    try {
      await AsyncStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(newUser));
      setUser(newUser);
      setIsLoading(false);
      return { success: true };
    } catch {
      setIsLoading(false);
      return { success: false, error: 'Failed to persist session.' };
    }
  };

  const signup = async (name: string, phone: string, password?: string) => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 600));

    if (!name.trim() || !phone.trim()) {
      setIsLoading(false);
      return { success: false, error: 'Name and phone number are required.' };
    }

    const newUser: AuthUser = {
      id: 'usr-' + Date.now(),
      name,
      phone,
      role: 'fisher',
      harbor: 'Versova',
    };

    try {
      await AsyncStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(newUser));
      setUser(newUser);
      setIsLoading(false);
      return { success: true };
    } catch {
      setIsLoading(false);
      return { success: false, error: 'Failed to create account.' };
    }
  };

  const loginAsDemo = async (persona: 'ramesh' | 'suresh') => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 400));

    const demoUser: AuthUser =
      persona === 'ramesh'
        ? {
            id: 'usr-ramesh-1',
            name: 'Ramesh Koli',
            phone: '9820012345',
            role: 'fisher',
            harbor: 'Versova',
          }
        : {
            id: 'usr-suresh-2',
            name: 'Suresh Patil',
            phone: '9820098765',
            role: 'captain',
            harbor: 'Sassoon Dock',
          };

    try {
      await AsyncStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(demoUser));
      setUser(demoUser);
    } catch (err) {
      console.warn('Failed to save demo user:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const resetPassword = async (identifier: string) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      success: true,
      message: `Password reset instructions sent to ${identifier}.`,
    };
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY_AUTH);
      setUser(null);
    } catch (err) {
      console.warn('Failed to remove auth session:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        loginAsDemo,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

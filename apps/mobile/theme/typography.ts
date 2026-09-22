/**
 * ORCA Maritime Design System — Typography
 * Optimized for Devanagari (Marathi/Hindi) and English legibility under motion and bright sunlight.
 * PRD 9.4: Increased line-heights to preserve legibility of conjunct characters, avoid clipping.
 */

import { TextStyle } from 'react-native';

export const typography = {
  // Headings
  h1: {
    fontSize: 28,
    fontWeight: '700' as const,
    lineHeight: 38,
    letterSpacing: 0.3,
  },
  h2: {
    fontSize: 22,
    fontWeight: '700' as const,
    lineHeight: 32,
    letterSpacing: 0.2,
  },
  h3: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 28,
    letterSpacing: 0.1,
  },

  // Body text — with generous line heights for Devanagari conjuncts
  bodyLarge: {
    fontSize: 17,
    fontWeight: '400' as const,
    lineHeight: 26,
  },
  bodyMedium: {
    fontSize: 15,
    fontWeight: '400' as const,
    lineHeight: 24,
  },
  bodySmall: {
    fontSize: 13,
    fontWeight: '400' as const,
    lineHeight: 20,
  },

  // Specialized Display
  metricValue: {
    fontSize: 32,
    fontWeight: '800' as const,
    lineHeight: 40,
  },
  metricUnit: {
    fontSize: 15,
    fontWeight: '500' as const,
    lineHeight: 22,
  },
  label: {
    fontSize: 13,
    fontWeight: '600' as const,
    lineHeight: 18,
    letterSpacing: 0.5,
    textTransform: 'uppercase' as const,
  },
  badge: {
    fontSize: 13,
    fontWeight: '700' as const,
    lineHeight: 18,
  },
  button: {
    fontSize: 16,
    fontWeight: '700' as const,
    lineHeight: 24,
    letterSpacing: 0.2,
  },
  buttonLarge: {
    fontSize: 18,
    fontWeight: '800' as const,
    lineHeight: 28,
    letterSpacing: 0.3,
  },
};

export type TypographyKeys = keyof typeof typography;

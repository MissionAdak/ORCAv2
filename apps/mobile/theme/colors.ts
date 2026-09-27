/**
 * ORCA Maritime Design System — Color Palette
 * Designed for high-glare sunlight, night visibility, and maritime safety.
 * Based on PRD Section 9.4 (Maritime Design System & Accessibility).
 */

export const colors = {
  // Deep maritime backgrounds (avoids sunlight glare & washout)
  backgroundDark: '#0A1128',
  backgroundNavy: '#001F54',
  backgroundCard: '#0E2A47',
  backgroundCardElevated: '#163B66',
  surfaceBorder: '#1F4E79',
  surfaceBorderActive: '#3A7CA5',

  // High-luminance foregrounds for direct sunlight
  textPrimary: '#FFFFFF',
  textSecondary: '#B0C4DE',
  textMuted: '#6B829E',
  textInverted: '#0A1128',

  // Primary brand / maritime accent
  accentBlue: '#00A8E8',
  accentTeal: '#007EA7',
  accentGold: '#FFB703', // High-visibility amber

  // Safety & Risk Levels (Always paired with icon + text label)
  riskLow: '#2A9D8F',       // Green (0-30)
  riskModerate: '#FFB703',  // Amber / Yellow (31-60)
  riskHigh: '#E63946',      // Red (61-100)

  // Emergency / SOS Palette (High contrast alert)
  sosBackground: '#8B0000',
  sosBright: '#FF0033',
  sosForeground: '#FFFFFF',
  sosHighlight: '#FFD700',

  // System states
  staleBackground: '#3D2800',
  staleText: '#FFC837',
  staleBorder: '#8A5D00',

  offlineBackground: '#262A30',
  offlineText: '#D1D5DB',
  offlineBorder: '#4B5563',

  // Utility colors
  divider: '#1E3A5F',
  overlay: 'rgba(0, 8, 20, 0.75)',
};

export type ColorKeys = keyof typeof colors;

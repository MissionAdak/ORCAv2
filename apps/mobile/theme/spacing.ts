/**
 * ORCA Maritime Design System — Spacing & Touch Targets
 * PRD Section 9.4: Minimum tap target size of 64dp x 64dp in Wet-Hand & Glare Mode.
 */

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,

  // Touch Target Standards
  touchTargetStandard: 48,
  touchTargetWetHand: 64, // PRD Differentiator 5 requirement

  // Border Radius
  radiusSm: 6,
  radiusMd: 12,
  radiusLg: 18,
  radiusFull: 9999,
};

export type SpacingKeys = keyof typeof spacing;

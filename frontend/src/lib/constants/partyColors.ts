/**
 * Australian Political Party Colors
 *
 * A centralized map of party names to their official/recognized brand colors.
 * Used for consistent party identification across components.
 */

export const PARTY_COLORS: Record<string, string> = {
  // Major Parties
  Labor: '#e53935',
  'Australian Labor Party': '#e53935',
  ALP: '#e53935',
  Liberal: '#1e40af',
  'Liberal Party': '#1e40af',
  'Liberal Party of Australia': '#1e40af',
  National: '#006644',
  Nationals: '#006644',
  'National Party': '#006644',
  'National Party of Australia': '#006644',
  'Liberal National': '#1e40af',
  'Liberal National Party': '#1e40af',
  LNP: '#1e40af',
  Coalition: '#1e40af',

  // Greens
  Greens: '#10b981',
  'Australian Greens': '#10b981',
  'The Greens': '#10b981',

  // Minor Parties
  'One Nation': '#f97316',
  "Pauline Hanson's One Nation": '#f97316',
  PHON: '#f97316',
  'United Australia Party': '#fbbf24',
  UAP: '#fbbf24',
  "Katter's Australian Party": '#8b0000',
  KAP: '#8b0000',
  'Centre Alliance': '#00bcd4',
  'Jacqui Lambie Network': '#9c27b0',
  JLN: '#9c27b0',

  // Teals & Independents
  Teal: '#14b8a6',
  'Teal Independent': '#14b8a6',
  Independent: '#6b7280',
  IND: '#6b7280',
};

export const DEFAULT_PARTY_COLOR = '#6b7280';

/**
 * Get the color for a political party.
 * Returns the default gray color if party is not recognized.
 */
export function getPartyColor(party: string): string {
  return PARTY_COLORS[party] ?? DEFAULT_PARTY_COLOR;
}

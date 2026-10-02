// Countries where Enable Banking offers bank connections (EEA + UK), ISO 3166-1 alpha-2
export const BANK_COUNTRIES = [
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS", "IE", "IT",
  "LV", "LI", "LT", "LU", "MT", "NL", "NO", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "GB",
] as const

export const DEFAULT_BANK_COUNTRY = "GR"

const COUNTRY_NAMES = new Intl.DisplayNames(undefined, { type: "region" })

export function countryName(code: string): string {
  return COUNTRY_NAMES.of(code) ?? code
}

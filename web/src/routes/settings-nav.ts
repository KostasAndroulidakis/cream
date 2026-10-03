import { paths } from "./paths"

export type SettingsItem = {
  label: string
  // Not built yet when missing: shown, but marked coming soon
  to?: string
  beta?: boolean
}

export type SettingsGroup = { title: string; items: readonly SettingsItem[] }

/**
 * Monarch's settings menu, in its order. Monarch's billing, gifting, referral and early access
 * pages are left out: CREAM has nothing to sell.
 */
export const SETTINGS_GROUPS: readonly SettingsGroup[] = [
  {
    title: "Account",
    items: [
      { label: "Profile", to: paths.settingsProfile },
      { label: "Display" },
      { label: "Notifications" },
      { label: "Security" },
      { label: "Integrations", beta: true },
    ],
  },
  {
    title: "Household",
    items: [
      { label: "General" },
      { label: "Businesses" },
      { label: "Members" },
      { label: "Preferences" },
      // Already built as their own pages
      { label: "Institutions", to: paths.connections },
      { label: "Categories" },
      { label: "Merchants" },
      { label: "Rules", to: paths.review },
      { label: "Tags" },
      { label: "Data" },
    ],
  },
]

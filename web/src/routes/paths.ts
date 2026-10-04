export const paths = {
  home: "/",
  accounts: "/accounts",
  transactions: "/transactions",
  review: "/review",
  // Banks used to live here; old links land on Settings › Institutions
  connections: "/connections",
  settings: "/settings",
  settingsProfile: "/settings/profile",
  settingsInstitutions: "/settings/institutions",
  settingsCategories: "/settings/categories",
  settingsMerchants: "/settings/merchants",
  // Must match CREAM_ENABLEBANKING_REDIRECT_URL and the redirect URL registered at the provider
  connectionCallback: "/connections/callback",
  login: "/login",
  signup: "/signup",
} as const

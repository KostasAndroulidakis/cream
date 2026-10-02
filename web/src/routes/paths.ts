export const paths = {
  home: "/",
  connections: "/connections",
  // Must match CREAM_ENABLEBANKING_REDIRECT_URL and the redirect URL registered at the provider
  connectionCallback: "/connections/callback",
  login: "/login",
  signup: "/signup",
} as const

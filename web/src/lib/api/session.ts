/** Query key of the signed-in user. Shared so any 401 can end the session in one place. */
export const SESSION_QUERY_KEY = ["auth", "me"] as const

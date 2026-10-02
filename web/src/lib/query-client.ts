import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query"

import { ApiError } from "./api/errors"
import { HTTP_STATUS } from "./api/http-status"
import { SESSION_QUERY_KEY } from "./api/session"

const DEFAULT_STALE_TIME_MS = 30_000

// Any 401 means the session cookie expired or was revoked: clearing the user
// makes the route guard send the person back to the login page.
function endSessionOnUnauthorized(error: unknown) {
  if (error instanceof ApiError && error.status === HTTP_STATUS.UNAUTHORIZED) {
    queryClient.setQueryData(SESSION_QUERY_KEY, null)
  }
}

export const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: endSessionOnUnauthorized }),
  mutationCache: new MutationCache({ onError: endSessionOnUnauthorized }),
  defaultOptions: {
    queries: { staleTime: DEFAULT_STALE_TIME_MS },
  },
})

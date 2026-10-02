import { Navigate, Outlet, useLocation } from "react-router"

import { FullPageMessage } from "@/components/full-page-message"
import { Button } from "@/components/ui/button"
import { useCurrentUser } from "@/features/auth/api"
import { paths } from "./paths"
import { redirectTarget, type RedirectState } from "./redirect"

/** Renders child routes only for signed-in users; everyone else goes to login. */
export function RequireAuth() {
  const location = useLocation()
  const { data: user, isPending, isError, refetch } = useCurrentUser()

  if (isPending) return <FullPageMessage title="Loading…" />
  if (isError) {
    return (
      <FullPageMessage title="Can't reach CREAM right now.">
        <Button variant="outline" onClick={() => refetch()}>
          Try again
        </Button>
      </FullPageMessage>
    )
  }
  if (!user) {
    const state: RedirectState = { from: location }
    return <Navigate to={paths.login} replace state={state} />
  }
  return <Outlet />
}

/** Keeps signed-in users away from login/signup, sending them where they were headed. */
export function RedirectIfAuthenticated() {
  const location = useLocation()
  const { data: user, isPending } = useCurrentUser()

  if (isPending) return <FullPageMessage title="Loading…" />
  if (user) return <Navigate to={redirectTarget(location)} replace />
  return <Outlet />
}

import { LogOut } from "lucide-react"

import { Button } from "@/components/ui/button"
import { displayNameOf, useCurrentUser, useLogout } from "@/features/auth/api"

/** Who is signed in, and the way out; `compact` keeps only the log out icon, for the collapsed sidebar. */
export function AccountActions({ compact = false }: { compact?: boolean }) {
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  if (compact) {
    return (
      <div className="flex justify-center">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => logout.mutate()}
          disabled={logout.isPending}
          aria-label="Log out"
          title="Log out"
        >
          <LogOut aria-hidden />
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between gap-2">
      <span className="truncate px-3 text-sm text-muted-foreground">{user && displayNameOf(user)}</span>
      <Button variant="ghost" size="sm" onClick={() => logout.mutate()} disabled={logout.isPending}>
        <LogOut aria-hidden />
        {logout.isPending ? "Logging out…" : "Log out"}
      </Button>
    </div>
  )
}

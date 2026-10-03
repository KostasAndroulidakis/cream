import { LogOut } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"

/** Who is signed in, and the way out. */
export function AccountActions() {
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  return (
    <div className="flex items-center justify-between gap-2">
      <span className="truncate px-3 text-sm text-muted-foreground">{user?.first_name}</span>
      <Button variant="ghost" size="sm" onClick={() => logout.mutate()} disabled={logout.isPending}>
        <LogOut aria-hidden />
        {logout.isPending ? "Logging out…" : "Log out"}
      </Button>
    </div>
  )
}

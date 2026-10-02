import type { ComponentType } from "react"
import { NavLink, Outlet } from "react-router"

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"
import { InboxCountBadge } from "@/features/categorization/components/inbox-count-badge"
import { cn } from "@/lib/utils"
import { paths } from "./paths"

type NavItem = {
  to: string
  label: string
  end: boolean
  // Optional live indicator next to the label
  Badge?: ComponentType
}

const NAV_ITEMS: readonly NavItem[] = [
  { to: paths.home, label: "Overview", end: true },
  { to: paths.review, label: "Review", end: false, Badge: InboxCountBadge },
  { to: paths.connections, label: "Banks", end: false },
]

/** Shell for every signed-in page: header with navigation and account actions. */
export function AppLayout() {
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  return (
    <div className="min-h-svh bg-muted/40">
      <header className="border-b bg-background">
        {/* On phones the navigation drops to its own row so nothing overflows */}
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-8 px-4 sm:h-14 sm:flex-nowrap sm:px-6">
          <span className="flex h-12 items-center text-lg font-semibold tracking-tight sm:h-auto">CREAM</span>
          <nav aria-label="Main" className="order-last -mx-3 flex w-full items-center gap-1 pb-2 sm:order-none sm:mx-0 sm:w-auto sm:pb-0">
            {NAV_ITEMS.map(({ to, label, end, Badge }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground",
                    isActive && "bg-muted text-foreground",
                  )
                }
              >
                {label}
                {Badge && <Badge />}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-sm text-muted-foreground sm:inline">{user?.first_name}</span>
            <Button variant="ghost" onClick={() => logout.mutate()} disabled={logout.isPending}>
              {logout.isPending ? "Logging out…" : "Log out"}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>
    </div>
  )
}

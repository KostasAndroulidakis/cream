import { NavLink, Outlet } from "react-router"

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"
import { cn } from "@/lib/utils"
import { paths } from "./paths"

const NAV_ITEMS = [
  { to: paths.home, label: "Overview", end: true },
  { to: paths.connections, label: "Banks", end: false },
] as const

/** Shell for every signed-in page: header with navigation and account actions. */
export function AppLayout() {
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  return (
    <div className="min-h-svh bg-muted/40">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-6 px-6">
          <div className="flex items-center gap-8">
            <span className="text-lg font-semibold tracking-tight">CREAM</span>
            <nav aria-label="Main" className="flex items-center gap-1">
              {NAV_ITEMS.map(({ to, label, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    cn(
                      "rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground",
                      isActive && "bg-muted text-foreground",
                    )
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-muted-foreground sm:inline">{user?.first_name}</span>
            <Button variant="ghost" onClick={() => logout.mutate()} disabled={logout.isPending}>
              {logout.isPending ? "Logging out…" : "Log out"}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  )
}

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"
import { SystemStatus } from "@/features/health/components/system-status"

export function HomePage() {
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  return (
    <div className="min-h-svh bg-muted/40">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <span className="text-lg font-semibold tracking-tight">CREAM</span>
          <Button variant="ghost" onClick={() => logout.mutate()} disabled={logout.isPending}>
            {logout.isPending ? "Logging out…" : "Log out"}
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-8 px-6 py-10">
        <div className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Hi, {user?.first_name}.</h1>
          <p className="text-muted-foreground">Your wallets will show up here once you add one.</p>
        </div>
        <div className="max-w-sm">
          <SystemStatus />
        </div>
      </main>
    </div>
  )
}

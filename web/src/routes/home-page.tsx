import { useQuery } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"
import { SystemStatus } from "@/features/health/components/system-status"
import { walletsQueryOptions } from "@/features/wallets/api"
import { CreateWalletDialog } from "@/features/wallets/components/create-wallet-dialog"
import { CurrencyTotals } from "@/features/wallets/components/currency-totals"
import { WalletList } from "@/features/wallets/components/wallet-list"

export function HomePage() {
  const { data: user } = useCurrentUser()
  const { data: wallets } = useQuery(walletsQueryOptions)
  const logout = useLogout()
  const hasWallets = (wallets?.length ?? 0) > 0

  return (
    <div className="min-h-svh bg-muted/40">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-6">
          <span className="text-lg font-semibold tracking-tight">CREAM</span>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-muted-foreground sm:inline">{user?.first_name}</span>
            <Button variant="ghost" onClick={() => logout.mutate()} disabled={logout.isPending}>
              {logout.isPending ? "Logging out…" : "Log out"}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl space-y-10 px-6 py-10">
        <CurrencyTotals />

        <section aria-labelledby="wallets-heading" className="rounded-xl border bg-card px-6 py-5 shadow-xs">
          <div className="flex items-center justify-between gap-4">
            <h2 id="wallets-heading" className="text-lg font-semibold tracking-tight">
              Wallets
            </h2>
            {hasWallets && <CreateWalletDialog />}
          </div>
          <div className="mt-2">
            <WalletList />
          </div>
        </section>

        <div className="max-w-sm">
          <SystemStatus />
        </div>
      </main>
    </div>
  )
}

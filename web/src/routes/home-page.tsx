import type { ReactNode } from "react"
import { useQuery } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { useCurrentUser, useLogout } from "@/features/auth/api"
import { SystemStatus } from "@/features/health/components/system-status"
import { CreateTransactionDialog } from "@/features/transactions/components/create-transaction-dialog"
import { RecentTransactions } from "@/features/transactions/components/recent-transactions"
import { CreateWalletDialog } from "@/features/wallets/components/create-wallet-dialog"
import { CurrencyTotals } from "@/features/wallets/components/currency-totals"
import { walletsQueryOptions } from "@/features/wallets/api"
import { WalletList } from "@/features/wallets/components/wallet-list"

function Panel({ id, title, action, children }: { id: string; title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section aria-labelledby={id} className="rounded-xl border bg-card px-6 py-5 shadow-xs">
      <div className="flex min-h-8 items-center justify-between gap-4">
        <h2 id={id} className="text-lg font-semibold tracking-tight">
          {title}
        </h2>
        {action}
      </div>
      <div className="mt-2">{children}</div>
    </section>
  )
}

export function HomePage() {
  const { data: user } = useCurrentUser()
  const { data: wallets } = useQuery(walletsQueryOptions)
  const logout = useLogout()
  const hasWallets = (wallets?.length ?? 0) > 0

  return (
    <div className="min-h-svh bg-muted/40">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <span className="text-lg font-semibold tracking-tight">CREAM</span>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-muted-foreground sm:inline">{user?.first_name}</span>
            <Button variant="ghost" onClick={() => logout.mutate()} disabled={logout.isPending}>
              {logout.isPending ? "Logging out…" : "Log out"}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-8 px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <CurrencyTotals />
          <CreateTransactionDialog />
        </div>

        <div className="grid items-start gap-6 lg:grid-cols-[3fr_2fr]">
          <Panel id="transactions-heading" title="Recent transactions">
            <RecentTransactions />
          </Panel>
          <Panel id="wallets-heading" title="Wallets" action={hasWallets && <CreateWalletDialog />}>
            <WalletList />
          </Panel>
        </div>

        <div className="max-w-sm">
          <SystemStatus />
        </div>
      </main>
    </div>
  )
}

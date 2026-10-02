import { useQuery } from "@tanstack/react-query"

import { PageColumns } from "@/components/page-columns"
import { Panel } from "@/components/panel"
import { SystemStatus } from "@/features/health/components/system-status"
import { CreateTransactionDialog } from "@/features/transactions/components/create-transaction-dialog"
import { RecentTransactions } from "@/features/transactions/components/recent-transactions"
import { walletsQueryOptions } from "@/features/wallets/api"
import { CreateWalletDialog } from "@/features/wallets/components/create-wallet-dialog"
import { CurrencyTotals } from "@/features/wallets/components/currency-totals"
import { WalletList } from "@/features/wallets/components/wallet-list"

export function HomePage() {
  const { data: wallets } = useQuery(walletsQueryOptions)
  const hasWallets = (wallets?.length ?? 0) > 0

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <CurrencyTotals />
        <CreateTransactionDialog />
      </div>

      <PageColumns>
        <Panel id="transactions-heading" title="Recent transactions">
          <RecentTransactions />
        </Panel>
        <Panel id="wallets-heading" title="Wallets" action={hasWallets && <CreateWalletDialog />}>
          <WalletList />
        </Panel>
      </PageColumns>

      <div className="max-w-sm">
        <SystemStatus />
      </div>
    </div>
  )
}

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { CheckboxField } from "@/components/checkbox-field"
import { PageColumns } from "@/components/page-columns"
import { PageHeader } from "@/components/page-header"
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
  const [showHidden, setShowHidden] = useState(false)

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" actions={<CreateTransactionDialog />} />
      <CurrencyTotals />

      <PageColumns>
        <Panel
          id="transactions-heading"
          title="Recent transactions"
          action={
            <CheckboxField checked={showHidden} onCheckedChange={setShowHidden}>
              Show hidden
            </CheckboxField>
          }
        >
          <RecentTransactions showHidden={showHidden} />
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

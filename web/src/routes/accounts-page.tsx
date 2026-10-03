import { ListFilter, Pencil } from "lucide-react"

import { ComingSoonButton } from "@/components/coming-soon-button"
import { PageColumns } from "@/components/page-columns"
import { PageHeader, PageHeaderDivider } from "@/components/page-header"
import { RefreshAllButton } from "@/features/bank/components/refresh-all-button"
import { CreateWalletDialog } from "@/features/wallets/components/create-wallet-dialog"
import { AccountGroups } from "@/features/wallets/components/account-groups"
import { NetWorthCard } from "@/features/wallets/components/net-worth-card"
import { SummaryCard } from "@/features/wallets/components/summary-card"

export function AccountsPage() {
  return (
    <div className="space-y-4">
      <PageHeader
        title="Accounts"
        actions={
          <>
            <ComingSoonButton icon={ListFilter}>Filters</ComingSoonButton>
            <PageHeaderDivider />
            <ComingSoonButton icon={Pencil}>Edit owners</ComingSoonButton>
            <RefreshAllButton />
            <CreateWalletDialog />
          </>
        }
      />
      <NetWorthCard />
      <PageColumns layout="summary">
        <AccountGroups />
        <SummaryCard />
      </PageColumns>
    </div>
  )
}

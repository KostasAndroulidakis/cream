import { ListFilter, Pencil } from "lucide-react"

import { ComingSoonButton } from "@/components/coming-soon-button"
import { PageColumns } from "@/components/page-columns"
import { PageHeader, PageHeaderDivider } from "@/components/page-header"
import { RefreshAllButton } from "@/features/bank/components/refresh-all-button"
import { AccountGroups } from "@/features/wallets/components/account-groups"
import { AddAccountDialog } from "@/features/wallets/components/add-account/add-account-dialog"
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
            <AddAccountDialog />
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

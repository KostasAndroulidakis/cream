import { ListFilter, Pencil } from "lucide-react"

import { ComingSoonButton } from "@/components/coming-soon-button"
import { PageHeader, PageHeaderDivider } from "@/components/page-header"
import { Surface } from "@/components/surface"
import { RefreshAllButton } from "@/features/bank/components/refresh-all-button"
import { CreateWalletDialog } from "@/features/wallets/components/create-wallet-dialog"
import { WalletList } from "@/features/wallets/components/wallet-list"

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
      <Surface label="Accounts list">
        <div className="px-6 py-2">
          <WalletList />
        </div>
      </Surface>
    </div>
  )
}

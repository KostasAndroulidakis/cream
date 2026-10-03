import { PageHeader } from "@/components/page-header"
import { ConnectBankForm } from "@/features/bank/components/connect-bank-form"
import { ConnectionList } from "@/features/bank/components/connection-list"
import { RefreshAllButton } from "@/features/bank/components/refresh-all-button"

export function ConnectionsPage() {
  return (
    <div className="space-y-8">
      <PageHeader title="Banks" actions={<RefreshAllButton />} />

      <section aria-labelledby="connected-heading" className="space-y-4">
        <h2 id="connected-heading" className="text-lg font-semibold tracking-tight">
          Connected banks
        </h2>
        <ConnectionList />
      </section>

      <section aria-labelledby="connect-heading" className="space-y-4 rounded-xl border bg-card px-6 py-5 shadow-xs">
        <div className="space-y-1">
          <h2 id="connect-heading" className="text-lg font-semibold tracking-tight">
            Connect a bank
          </h2>
          <p className="text-sm text-muted-foreground">
            Connect a bank once and CREAM imports its transactions. Access lasts up to 180 days, then you reconnect.
          </p>
        </div>
        <ConnectBankForm />
      </section>
    </div>
  )
}

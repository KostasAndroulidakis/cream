import { ConnectBankForm } from "@/features/bank/components/connect-bank-form"
import { ConnectionList } from "@/features/bank/components/connection-list"
import { SyncButton } from "@/features/bank/components/sync-button"

export function ConnectionsPage() {
  return (
    <div className="space-y-10">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-xl space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Banks</h1>
          <p className="text-muted-foreground">
            Connect a bank once and CREAM imports its transactions. Access lasts up to 180 days, then you reconnect.
          </p>
        </div>
        <SyncButton />
      </header>

      <section aria-labelledby="connected-heading" className="space-y-4">
        <h2 id="connected-heading" className="text-lg font-semibold tracking-tight">
          Connected banks
        </h2>
        <ConnectionList />
      </section>

      <section aria-labelledby="connect-heading" className="space-y-4 rounded-xl border bg-card px-6 py-5 shadow-xs">
        <h2 id="connect-heading" className="text-lg font-semibold tracking-tight">
          Connect a bank
        </h2>
        <ConnectBankForm />
      </section>
    </div>
  )
}

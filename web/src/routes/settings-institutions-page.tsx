import { InstitutionList } from "@/features/bank/components/institution-list"
import { RefreshAllButton } from "@/features/bank/components/refresh-all-button"
import { AddAccountDialog } from "@/features/wallets/components/add-account/add-account-dialog"

/** Settings › Institutions: the connected banks and their accounts, like Monarch's. */
export function SettingsInstitutionsPage() {
  return (
    <div className="space-y-4">
      <section aria-labelledby="institutions-heading" className="rounded-xl border bg-card shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b px-6 py-4">
          <h2 id="institutions-heading" className="text-lg font-medium tracking-tight">
            Institutions
          </h2>
          <div className="flex items-center gap-2 [&_button]:h-9">
            <RefreshAllButton />
            <AddAccountDialog />
          </div>
        </div>
        <p className="px-6 py-4.5">
          Link your bank accounts to get a complete view of your finances. CREAM only reads them, and access
          lasts up to 180 days before you reconnect.
        </p>
      </section>
      <InstitutionList />
    </div>
  )
}

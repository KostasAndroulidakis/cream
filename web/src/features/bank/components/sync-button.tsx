import { RefreshCw } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { useSyncBanks, type SyncResult } from "../api"

function summarize(results: SyncResult[]): string {
  if (results.length === 0) return "No linked accounts to sync yet."
  const imported = results.reduce((total, result) => total + result.imported, 0)
  return imported === 0 ? "Up to date. No new transactions." : `Imported ${imported} new transaction${imported === 1 ? "" : "s"}.`
}

export function SyncButton() {
  const sync = useSyncBanks()
  const failures = sync.data?.filter((result) => result.error) ?? []

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="outline" onClick={() => sync.mutate()} disabled={sync.isPending}>
          <RefreshCw className={cn(sync.isPending && "animate-spin")} aria-hidden />
          {sync.isPending ? "Syncing…" : "Sync now"}
        </Button>
        {sync.isSuccess && (
          <p className="text-sm text-muted-foreground" role="status">
            {summarize(sync.data)}
          </p>
        )}
      </div>
      {sync.isError && <FormAlert message={userMessage(sync.error)} />}
      {failures.map((result) => (
        <FormAlert key={result.bank_account_id} message={result.error ?? ""} />
      ))}
    </div>
  )
}

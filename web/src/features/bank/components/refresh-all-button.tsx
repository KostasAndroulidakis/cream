import { RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { notifyError, notifySuccess } from "@/lib/notify"
import { pluralize } from "@/lib/text"
import { cn } from "@/lib/utils"
import { useSyncBanks, type SyncResult } from "../api"

function summarize(results: SyncResult[]): string {
  if (results.length === 0) return "No linked accounts to sync yet."
  const imported = results.reduce((total, result) => total + result.imported, 0)
  const categorized = results.reduce((total, result) => total + result.categorized, 0)
  const parts = [imported === 0 ? "Up to date. No new transactions" : `Imported ${pluralize(imported, "new transaction")}`]
  if (categorized > 0) parts.push(`${categorized} categorized automatically`)
  return `${parts.join(", ")}.`
}

// One notification for the whole sync, plus one for each account that failed
function report(results: SyncResult[]) {
  notifySuccess({ title: "Accounts refreshed", description: summarize(results) })
  for (const result of results) {
    if (result.error) notifyError(result.error)
  }
}

/** "Refresh all": syncs every linked bank account now. */
export function RefreshAllButton() {
  const sync = useSyncBanks()

  return (
    <Button
      variant="outline"
      disabled={sync.isPending}
      onClick={() => sync.mutate(undefined, { onSuccess: report, onError: (error) => notifyError(userMessage(error)) })}
    >
      <RefreshCw className={cn(sync.isPending && "animate-spin")} aria-hidden />
      {sync.isPending ? "Refreshing…" : "Refresh all"}
    </Button>
  )
}

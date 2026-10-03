import { EyeOff } from "lucide-react"

import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { useSetTransactionHidden, type Transaction } from "../api"
import { transactionLabel } from "../display"

/**
 * Hides a transaction from lists and statistics (it still counts in the balance).
 * Shown on row hover or keyboard focus; always visible on touch screens, which have no hover.
 */
export function HideTransactionButton({ transaction }: { transaction: Transaction }) {
  const setHidden = useSetTransactionHidden()
  const label = transactionLabel(transaction) ?? "this transaction"

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      aria-label={`Hide ${label}`}
      title={setHidden.isError ? userMessage(setHidden.error) : "Hide (still counts in the balance)"}
      disabled={setHidden.isPending}
      onClick={() => setHidden.mutate({ transactionId: transaction.id, hidden: true })}
      className={cn(
        "text-muted-foreground opacity-0 transition-opacity group-hover/row:opacity-100 focus-visible:opacity-100 pointer-coarse:opacity-100",
        setHidden.isError && "text-destructive opacity-100",
      )}
    >
      <EyeOff aria-hidden />
    </Button>
  )
}

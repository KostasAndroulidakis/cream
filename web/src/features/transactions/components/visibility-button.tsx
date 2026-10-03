import { Eye, EyeOff } from "lucide-react"

import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { useSetTransactionHidden, type Transaction } from "../api"
import { transactionLabel } from "../display"

/**
 * Hides a transaction from lists and statistics (it still counts in the balance), or shows it again.
 * The hide button appears on row hover or keyboard focus, and always on touch screens (no hover there);
 * the show button is always visible, since a hidden row exists only to be brought back.
 */
export function VisibilityButton({ transaction }: { transaction: Transaction }) {
  const setHidden = useSetTransactionHidden()
  const label = transactionLabel(transaction) ?? "this transaction"
  const hidden = transaction.is_hidden
  const Icon = hidden ? Eye : EyeOff

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      aria-label={hidden ? `Show ${label}` : `Hide ${label}`}
      title={
        setHidden.isError
          ? userMessage(setHidden.error)
          : hidden
            ? "Show again"
            : "Hide: leave it out of lists and statistics (it still counts in the balance). " +
              "Money moved between your own accounts is a Transfer category instead."
      }
      disabled={setHidden.isPending}
      onClick={() => setHidden.mutate({ transactionId: transaction.id, hidden: !hidden })}
      className={cn(
        "text-muted-foreground transition-opacity",
        !hidden && "opacity-0 group-hover/row:opacity-100 focus-visible:opacity-100 pointer-coarse:opacity-100",
        setHidden.isError && "text-destructive opacity-100",
      )}
    >
      <Icon aria-hidden />
    </Button>
  )
}

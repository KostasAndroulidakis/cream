import { CircleCheck } from "lucide-react"

import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { useSetNeedsReview, type Transaction } from "../api"
import { transactionLabel, UNNAMED_TRANSACTION } from "../display"
import { REVEAL_ON_ROW_HOVER } from "../row-actions"

/** The ✓ on a row that needs review: one click marks it reviewed and takes it out of the inbox. */
export function MarkReviewedButton({ transaction }: { transaction: Transaction }) {
  const setNeedsReview = useSetNeedsReview()
  const label = transactionLabel(transaction) ?? UNNAMED_TRANSACTION

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      aria-label={`Mark ${label} as reviewed`}
      title={setNeedsReview.isError ? userMessage(setNeedsReview.error) : "Mark as reviewed"}
      disabled={setNeedsReview.isPending}
      onClick={() => setNeedsReview.mutate({ transactionId: transaction.id, needsReview: false })}
      className={cn(
        "text-muted-foreground hover:text-primary",
        REVEAL_ON_ROW_HOVER,
        setNeedsReview.isError && "text-destructive opacity-100",
      )}
    >
      <CircleCheck aria-hidden />
    </Button>
  )
}

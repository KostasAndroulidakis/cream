import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { notifyError, notifySuccess } from "@/lib/notify"
import { useMarkAllReviewed } from "../api"
import { markedReviewedNotice } from "../bulk-edit"

/** "Mark all N as reviewed": empties the review inbox in one click. */
export function MarkAllReviewedButton({ count }: { count: number }) {
  const markAll = useMarkAllReviewed()

  return (
    <Button
      size="lg"
      disabled={markAll.isPending}
      onClick={() =>
        markAll.mutate(undefined, {
          onSuccess: ({ affected }) => notifySuccess(markedReviewedNotice(affected)),
          onError: (error) => notifyError(userMessage(error)),
        })
      }
    >
      Mark all {count} as reviewed
    </Button>
  )
}

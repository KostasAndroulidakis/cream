import type { ReactNode } from "react"
import { Loader2 } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export type SummaryRow = { label: string; value: string }

type ConfirmChangesDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: ReactNode
  rows: SummaryRow[]
  confirmLabel: string
  isPending: boolean
  // Shown above the buttons when the last attempt failed
  errorMessage?: string
  onConfirm: () => void
}

/** "Does this look right?": the changes as rows, then Cancel or confirm (a spinner while it runs). */
export function ConfirmChangesDialog({
  open,
  onOpenChange,
  title,
  description,
  rows,
  confirmLabel,
  isPending,
  errorMessage,
  onConfirm,
}: ConfirmChangesDialogProps) {
  return (
    // While the change runs, the dialog stays open so the result is never missed
    <Dialog open={open} onOpenChange={(next) => isPending || onOpenChange(next)}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-lg">{title}</DialogTitle>
          <DialogDescription className="text-base text-foreground">{description}</DialogDescription>
        </DialogHeader>
        <dl className="-mx-4 divide-y border-y">
          {rows.map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between gap-6 px-4 py-3">
              <dt className="text-muted-foreground">{label}</dt>
              <dd className="truncate text-right">{value}</dd>
            </div>
          ))}
        </dl>
        {errorMessage && <FormAlert message={errorMessage} />}
        <DialogFooter className="border-t-0 bg-transparent pt-2">
          <DialogClose render={<Button variant="outline" size="lg" />} disabled={isPending}>
            Cancel
          </DialogClose>
          <Button size="lg" className="min-w-28" onClick={onConfirm} disabled={isPending}>
            {isPending ? <Loader2 className="animate-spin" aria-label="Applying changes" /> : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

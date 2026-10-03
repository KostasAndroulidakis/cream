import type { ReactNode } from "react"
import type { VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { Button, type buttonVariants } from "@/components/ui/button"
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

type ConfirmDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: ReactNode
  // What will change, as "field: value" rows; none for actions like deleting
  rows?: SummaryRow[]
  confirmLabel: string
  // "destructive" for actions that can't be undone
  confirmVariant?: VariantProps<typeof buttonVariants>["variant"]
  isPending: boolean
  // Shown above the buttons when the last attempt failed
  errorMessage?: string
  onConfirm: () => void
}

/** Asks before an action: optional rows of what changes, then Cancel or confirm (a spinner while it runs). */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  rows = [],
  confirmLabel,
  confirmVariant = "default",
  isPending,
  errorMessage,
  onConfirm,
}: ConfirmDialogProps) {
  return (
    // While the change runs, the dialog stays open so the result is never missed
    <Dialog open={open} onOpenChange={(next) => isPending || onOpenChange(next)}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-lg">{title}</DialogTitle>
          <DialogDescription className="text-base text-foreground">{description}</DialogDescription>
        </DialogHeader>
        {rows.length > 0 && (
          <dl className="-mx-4 divide-y border-y">
            {rows.map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between gap-6 px-4 py-3">
                <dt className="text-muted-foreground">{label}</dt>
                <dd className="truncate text-right">{value}</dd>
              </div>
            ))}
          </dl>
        )}
        {errorMessage && <FormAlert message={errorMessage} />}
        <DialogFooter className="border-t-0 bg-transparent pt-2">
          <DialogClose render={<Button variant="outline" size="lg" />} disabled={isPending}>
            Cancel
          </DialogClose>
          <Button size="lg" variant={confirmVariant} className="min-w-28" onClick={onConfirm} disabled={isPending}>
            {isPending ? <Loader2 className="animate-spin" aria-label="Applying changes" /> : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

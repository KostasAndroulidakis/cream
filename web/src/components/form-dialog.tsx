import type { FormEventHandler, ReactNode } from "react"

import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { cn } from "@/lib/utils"

type FormDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  // For screen readers; Monarch's dialogs show no subtitle
  description: string
  onSubmit: FormEventHandler<HTMLFormElement>
  children: ReactNode
  // The buttons at the bottom, e.g. Delete on the left, Cancel and Save on the right
  footer: ReactNode
}

/** Monarch's form dialog: title bar, the fields, and a footer of buttons, each part divided by a line. */
export function FormDialog({ open, onOpenChange, title, description, onSubmit, children, footer }: FormDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="gap-0 p-0 sm:max-w-[34rem] [&>[data-slot=dialog-close]]:top-4 [&>[data-slot=dialog-close]]:right-4">
        <div className="border-b px-6 py-5">
          <DialogTitle className="text-xl font-medium">{title}</DialogTitle>
          <DialogDescription className="sr-only">{description}</DialogDescription>
        </div>
        {/* React carries events up through portals: a dialog opened from another one submits only itself */}
        <form
          onSubmit={(event) => {
            event.stopPropagation()
            onSubmit(event)
          }}
          noValidate
        >
          <FormDialogBody>{children}</FormDialogBody>
          <FormDialogFooter>{footer}</FormDialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

/**
 * A dialog form's fields. Monarch's dialogs use larger text than the pages: 15px labels, 16px fields,
 * and every field the same 40px height.
 * Long forms (Edit Account) scroll between the fixed title bar and footer.
 */
export function FormDialogBody({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div
      className={cn(
        "max-h-[calc(100svh-11rem)] space-y-5 overflow-y-auto px-6 py-6 [&_[data-slot=label]]:text-[0.9375rem] [&_[data-slot=label]]:font-semibold [&_[data-slot=select-trigger]]:text-base [&_input]:h-10 [&_input]:text-base",
        className,
      )}
    >
      {children}
    </div>
  )
}

/** A dialog form's buttons, under a line: e.g. Delete on the left, Cancel and Save on the right. */
export function FormDialogFooter({ children }: { children: ReactNode }) {
  return <div className="flex items-center gap-3 border-t px-6 py-4 [&_button]:h-9">{children}</div>
}

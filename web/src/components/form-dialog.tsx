import type { FormEventHandler, ReactNode } from "react"

import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"

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
        <form onSubmit={onSubmit} noValidate>
          {/* Monarch's dialogs use larger text than the pages: 15px labels, 16px fields */}
          {/* Long forms (Edit Account) scroll between the fixed title bar and footer */}
          <div className="max-h-[calc(100svh-11rem)] space-y-5 overflow-y-auto px-6 py-6 [&_[data-slot=label]]:text-[0.9375rem] [&_[data-slot=label]]:font-semibold [&_[data-slot=select-trigger]]:text-base [&_input]:text-base">
            {children}
          </div>
          <div className="flex items-center gap-3 border-t px-6 py-4 [&_button]:h-9">{footer}</div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

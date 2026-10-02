import { useState } from "react"
import { Sparkles } from "lucide-react"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import type { Transaction } from "@/features/transactions/api"
import { transactionLabel } from "@/features/transactions/display"
import { isAutoCategorized } from "../sources"
import { CategorizeForm } from "./categorize-form"

type ChangeCategoryDialogProps = {
  transaction: Transaction
  categoryName: string
}

/** The transaction's category as a button that opens a picker to change it. */
export function ChangeCategoryDialog({ transaction, categoryName }: ChangeCategoryDialogProps) {
  const [open, setOpen] = useState(false)
  const automatic = isAutoCategorized(transaction)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <button
            type="button"
            title={automatic ? "Categorized automatically. Click to change." : "Change category"}
            className="inline-flex items-center gap-1 rounded-sm underline decoration-muted-foreground/40 decoration-dotted underline-offset-4 outline-none transition-colors hover:text-foreground hover:decoration-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        }
      >
        {automatic && <Sparkles className="size-3 text-brass" aria-label="Categorized automatically" />}
        {categoryName}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Change category</DialogTitle>
          <DialogDescription>
            {transactionLabel(transaction) ?? "This transaction"} is in {categoryName} now.
          </DialogDescription>
        </DialogHeader>
        {/* Unmounted on close, so the form starts fresh every time */}
        {open && <CategorizeForm transaction={transaction} layout="stacked" onCategorized={() => setOpen(false)} />}
      </DialogContent>
    </Dialog>
  )
}

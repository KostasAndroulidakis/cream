import { useState } from "react"
import { Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ConnectBankForm } from "./connect-bank-form"

/** "Add account" on Institutions: pick a bank, then log in on the bank's own page. */
export function AddInstitutionDialog() {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus aria-hidden />
        Add account
      </DialogTrigger>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Connect a bank</DialogTitle>
          <DialogDescription>
            Connect a bank once and CREAM imports its transactions. Access lasts up to 180 days, then you reconnect.
          </DialogDescription>
        </DialogHeader>
        {/* Unmounted on close, so the form starts fresh every time */}
        {open && <ConnectBankForm />}
      </DialogContent>
    </Dialog>
  )
}

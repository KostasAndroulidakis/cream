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
import { CreateWalletForm } from "./create-wallet-form"

export function CreateWalletDialog() {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus aria-hidden />
        Add account
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add an account</DialogTitle>
          <DialogDescription>
            Anywhere you keep money. Enter what's in it today; transactions take it from there.
          </DialogDescription>
        </DialogHeader>
        {/* Unmounted on close, so the form starts fresh every time */}
        {open && <CreateWalletForm onCreated={() => setOpen(false)} />}
      </DialogContent>
    </Dialog>
  )
}

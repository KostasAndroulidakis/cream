import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
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
import { walletsQueryOptions } from "@/features/wallets/api"
import { CreateTransactionForm } from "./create-transaction-form"

export function CreateTransactionDialog() {
  const [open, setOpen] = useState(false)
  const { data: wallets } = useQuery(walletsQueryOptions)
  const hasWallets = (wallets?.length ?? 0) > 0

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={<Button disabled={!hasWallets} title={hasWallets ? undefined : "Add an account first"} />}
      >
        <Plus aria-hidden />
        Add transaction
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add a transaction</DialogTitle>
          <DialogDescription>Money in or out of one of your accounts.</DialogDescription>
        </DialogHeader>
        {/* Unmounted on close, so the form starts fresh every time */}
        {open && <CreateTransactionForm onCreated={() => setOpen(false)} />}
      </DialogContent>
    </Dialog>
  )
}

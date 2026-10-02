import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { userMessage } from "@/lib/api/errors"
import { formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"
import { walletsQueryOptions, type Wallet } from "../api"
import { WALLET_TYPE_META } from "../wallet-types"
import { CreateWalletDialog } from "./create-wallet-dialog"

const SKELETON_ROWS = 3

function WalletRow({ wallet }: { wallet: Wallet }) {
  const { label, icon: Icon } = WALLET_TYPE_META[wallet.type]
  const isNegative = wallet.balance.startsWith("-")

  return (
    <li className="flex items-center gap-4 py-4">
      <span className="grid size-10 shrink-0 place-items-center rounded-full bg-primary/8 text-primary">
        <Icon className="size-5" aria-hidden />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{wallet.name}</p>
        <p className="text-sm text-muted-foreground">{label}</p>
      </div>
      <p className={cn("font-medium tabular-nums", isNegative && "text-destructive")}>
        {formatMoney(wallet.balance, wallet.currency)}
      </p>
    </li>
  )
}

export function WalletList() {
  const { data: wallets, isPending, isError, error } = useQuery(walletsQueryOptions)

  if (isPending) {
    return (
      <ul className="divide-y" aria-label="Loading wallets">
        {Array.from({ length: SKELETON_ROWS }, (_, i) => (
          <li key={i} className="h-[4.5rem] animate-pulse py-4">
            <div className="h-full rounded-lg bg-muted" />
          </li>
        ))}
      </ul>
    )
  }

  if (isError) return <FormAlert message={userMessage(error)} />

  if (wallets.length === 0) {
    return (
      <div className="rounded-xl border border-dashed px-6 py-10 text-center">
        <p className="font-medium">No wallets yet</p>
        <p className="mx-auto mt-1 max-w-xs text-sm text-muted-foreground">
          Add your bank account, the cash in your pocket, or a stash to start tracking.
        </p>
        <div className="mt-5">
          <CreateWalletDialog />
        </div>
      </div>
    )
  }

  return (
    <ul className="divide-y">
      {wallets.map((wallet) => (
        <WalletRow key={wallet.id} wallet={wallet} />
      ))}
    </ul>
  )
}

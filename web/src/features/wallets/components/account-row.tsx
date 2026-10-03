import { formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"
import type { Wallet } from "../api"
import { ACCOUNT_TYPE_ICONS } from "../wallet-types"

// The skeleton rows use it too, so the page doesn't jump when the list arrives
export const ACCOUNT_ROW_HEIGHT = "h-[4.5rem]"

type AccountRowProps = {
  wallet: Wallet
  // The subtype, e.g. "Checking", shown under the name as Monarch does
  label: string
}

/** One account: its type's icon, name and subtype, and its balance. */
export function AccountRow({ wallet, label }: AccountRowProps) {
  const Icon = ACCOUNT_TYPE_ICONS[wallet.type]
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

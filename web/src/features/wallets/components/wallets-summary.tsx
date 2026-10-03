import { pluralize } from "@/lib/text"
import type { Wallet } from "../api"
import { ACCOUNT_TYPE_ICONS } from "../wallet-types"

// More icons than this would only overlap into noise
const MAX_ICONS = 3

/** "2 accounts selected" with overlapping wallet icons and the wallet names below. */
export function WalletsSummary({ wallets }: { wallets: Wallet[] }) {
  return (
    <div className="flex items-center gap-4 bg-sidebar px-6 py-5">
      <div className="flex shrink-0 -space-x-3">
        {wallets.slice(0, MAX_ICONS).map((wallet) => {
          const Icon = ACCOUNT_TYPE_ICONS[wallet.type]
          return (
            <span
              key={wallet.id}
              className="grid size-11 place-items-center rounded-full border-2 border-sidebar bg-primary/10 text-primary"
            >
              <Icon className="size-5" aria-hidden />
            </span>
          )
        })}
      </div>
      <div className="min-w-0">
        <p className="text-base font-semibold">{pluralize(wallets.length, "account")} selected</p>
        <p className="truncate text-sm text-muted-foreground">{wallets.map((wallet) => wallet.name).join(", ")}</p>
      </div>
    </div>
  )
}

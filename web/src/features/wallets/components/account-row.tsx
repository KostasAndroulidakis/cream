import { Amount } from "@/components/amount"
import { cn } from "@/lib/utils"
import type { Wallet } from "../api"
import { ACCOUNT_TYPE_ICONS } from "../wallet-types"

// The skeleton rows use it too, so the page doesn't jump when the list arrives
export const ACCOUNT_ROW_HEIGHT = "h-[4.5rem]"

type AccountRowProps = {
  wallet: Wallet
  // The subtype, e.g. "Checking", shown under the name as Monarch does
  label: string
  // Makes the whole row a button (e.g. opening Edit Account)
  onSelect?: () => void
}

/** One account: its type's icon, name and subtype, and its balance. */
export function AccountRow({ wallet, label, onSelect }: AccountRowProps) {
  const content = (
    <>
      <AccountTypeIcon wallet={wallet} />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{wallet.name}</p>
        <p className="text-sm text-muted-foreground">{label}</p>
      </div>
      <Amount value={wallet.balance} currency={wallet.currency} kind="balance" className="font-medium" />
    </>
  )

  return (
    <li>
      {onSelect ? (
        <button
          type="button"
          onClick={onSelect}
          className="-mx-6 flex w-[calc(100%+3rem)] items-center gap-4 px-6 py-4 text-left hover:bg-sidebar/60"
        >
          {content}
        </button>
      ) : (
        <div className="flex items-center gap-4 py-4">{content}</div>
      )}
    </li>
  )
}

/** The round icon of the account's type, e.g. $ for Cash. */
export function AccountTypeIcon({ wallet, className }: { wallet: Wallet; className?: string }) {
  const Icon = ACCOUNT_TYPE_ICONS[wallet.type]
  return (
    <span
      className={cn("grid size-10 shrink-0 place-items-center rounded-full bg-primary/8 text-primary", className)}
    >
      {/* Half the badge, so the icon scales with it (a row's 40px badge, a transaction's 24px one) */}
      <Icon className="size-1/2" aria-hidden />
    </span>
  )
}

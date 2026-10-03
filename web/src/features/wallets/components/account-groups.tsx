import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { ChevronDown } from "lucide-react"

import { AmountTotals } from "@/components/amount"
import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { Surface } from "@/components/surface"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { walletsQueryOptions } from "../api"
import { groupByType, type AccountGroup } from "../grouping"
import { useAccountTypes } from "../use-account-types"
import { ACCOUNT_ROW_HEIGHT, AccountRow } from "./account-row"
import { NoAccounts } from "./no-accounts"

const SKELETON_ROWS = 3

/** One type's card: a header that folds the list away, with the type's total, then its accounts. */
function AccountGroupCard({ group }: { group: AccountGroup }) {
  const [open, setOpen] = useState(true)
  const { subtypeLabel } = useAccountTypes()
  const listId = `accounts-${group.info.type}`

  return (
    <Surface label={group.info.label}>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-3 px-6 py-4 text-left hover:bg-sidebar/60"
      >
        <ChevronDown
          className={cn("size-4 text-muted-foreground transition-transform", !open && "-rotate-90")}
          aria-hidden
        />
        <h2 className="flex-1 text-lg font-semibold tracking-tight">{group.info.label}</h2>
        <AmountTotals totals={group.totals} kind="balance" className="text-lg font-semibold" />
      </button>
      {open && (
        <ul id={listId} className="divide-y border-t px-6">
          {group.wallets.map((wallet) => (
            <AccountRow key={wallet.id} wallet={wallet} label={subtypeLabel(wallet.type, wallet.subtype)} />
          ))}
        </ul>
      )}
    </Surface>
  )
}

/** The Accounts page's list: one card per type (Cash, Investments, … Loans), in Monarch's order. */
export function AccountGroups() {
  const { data: wallets, isPending, isError, error } = useQuery(walletsQueryOptions)
  const { catalog } = useAccountTypes()

  if (isPending) {
    return (
      <Surface label="Loading accounts">
        <div className="px-6">
          <ListSkeleton rows={SKELETON_ROWS} label="Loading accounts" rowClassName={ACCOUNT_ROW_HEIGHT} />
        </div>
      </Surface>
    )
  }
  if (isError) return <FormAlert message={userMessage(error)} />
  if (wallets.length === 0) return <NoAccounts />

  return (
    <div className="space-y-4">
      {/* "Hide account" leaves it off this page */}
      {groupByType(
        wallets.filter((wallet) => !wallet.is_hidden),
        catalog,
      ).map((group) => (
        <AccountGroupCard key={group.info.type} group={group} />
      ))}
    </div>
  )
}

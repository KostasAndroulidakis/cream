import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { userMessage } from "@/lib/api/errors"
import { walletsQueryOptions } from "../api"
import { useAccountTypes } from "../use-account-types"
import { ACCOUNT_ROW_HEIGHT, AccountRow } from "./account-row"
import { NoAccounts } from "./no-accounts"

const SKELETON_ROWS = 3

/** Every account in one list (the dashboard's), oldest first. */
export function WalletList() {
  const { data: wallets, isPending, isError, error } = useQuery(walletsQueryOptions)
  const { subtypeLabel } = useAccountTypes()

  if (isPending) return <ListSkeleton rows={SKELETON_ROWS} label="Loading accounts" rowClassName={ACCOUNT_ROW_HEIGHT} />
  if (isError) return <FormAlert message={userMessage(error)} />
  if (wallets.length === 0) return <NoAccounts />

  return (
    <ul className="divide-y">
      {/* "Hide account" leaves it off the account lists, nothing else */}
      {wallets
        .filter((wallet) => !wallet.is_hidden)
        .map((wallet) => (
        <AccountRow key={wallet.id} wallet={wallet} label={subtypeLabel(wallet.type, wallet.subtype)} />
      ))}
    </ul>
  )
}

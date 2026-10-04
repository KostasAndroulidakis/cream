import { useQuery } from "@tanstack/react-query"

import type { Wallet } from "@/features/wallets/api"
import { AccountTypeIcon } from "@/features/wallets/components/account-row"
import { connectionsQueryOptions } from "../api"
import { InstitutionLogo } from "./institution-logo"

/** An account's mark, as Monarch shows it next to its name: its bank's logo, or its type's icon when added by hand. */
export function AccountLogo({ wallet, className }: { wallet: Wallet; className?: string }) {
  const { data: connections = [] } = useQuery(connectionsQueryOptions)
  const connection = connections.find((each) => each.accounts.some((account) => account.wallet_id === wallet.id))
  if (connection) return <InstitutionLogo connection={connection} className={className} />
  return <AccountTypeIcon wallet={wallet} className={className} />
}

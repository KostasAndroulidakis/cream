import { totalsByCurrency, type CurrencyTotal } from "@/lib/currency-totals"
import type { AccountTypeInfo, Wallet } from "./api"

export type AccountGroup = {
  info: AccountTypeInfo
  wallets: Wallet[]
  // The group's balance per currency (currencies are never mixed)
  totals: CurrencyTotal[]
}

/** Accounts under their type, in Monarch's order (the catalog's); types without accounts are left out. */
export function groupByType(wallets: readonly Wallet[], catalog: readonly AccountTypeInfo[]): AccountGroup[] {
  return catalog
    .map((info) => {
      const members = wallets.filter((wallet) => wallet.type === info.type)
      const totals = totalsByCurrency(members.map((wallet) => ({ currency: wallet.currency, amount: wallet.balance })))
      return { info, wallets: members, totals }
    })
    .filter((group) => group.wallets.length > 0)
}

import type { CurrencyTotal } from "@/lib/currency-totals"
import type { AccountTypeInfo, AccountsSummary, Wallet } from "./api"

export type AccountGroup = {
  info: AccountTypeInfo
  wallets: Wallet[]
  // The group's balance per currency, as the API counts it (excluded balances left out)
  totals: CurrencyTotal[]
}

/** The API's totals ({currency, balance}) in the shape the amount components take. */
export function toCurrencyTotals(totals: AccountsSummary["net_worth"]): CurrencyTotal[] {
  return totals.map(({ currency, balance }) => ({ currency, amount: balance }))
}

/** Accounts under their type, in Monarch's order (the catalog's); types without accounts are left out. */
export function groupByType(
  wallets: readonly Wallet[],
  catalog: readonly AccountTypeInfo[],
  summary: AccountsSummary | undefined,
): AccountGroup[] {
  const totalsByType = new Map(summary?.types.map((total) => [total.type, toCurrencyTotals(total.totals)]))
  return catalog
    .map((info) => ({
      info,
      wallets: wallets.filter((wallet) => wallet.type === info.type),
      totals: totalsByType.get(info.type) ?? [],
    }))
    .filter((group) => group.wallets.length > 0)
}

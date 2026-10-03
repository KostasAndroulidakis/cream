import { sumAmounts } from "@/lib/decimal"
import { localDayKey } from "@/lib/dates"
import type { Transaction } from "./api"

export type CurrencyTotal = { currency: string; amount: string }

export type DayGroup = {
  // YYYY-MM-DD in the user's time zone
  day: string
  transactions: Transaction[]
  // Net of the day per currency (currencies are never mixed); hidden transactions don't count
  totals: CurrencyTotal[]
}

/** Consecutive transactions (newest first, as the API lists them) grouped by calendar day. */
export function groupByDay(
  transactions: readonly Transaction[],
  currencyOf: (walletId: number) => string | undefined,
): DayGroup[] {
  const groups: DayGroup[] = []
  for (const transaction of transactions) {
    const day = localDayKey(transaction.occurred_at)
    const last = groups.at(-1)
    if (last?.day === day) last.transactions.push(transaction)
    else groups.push({ day, transactions: [transaction], totals: [] })
  }
  for (const group of groups) group.totals = dayTotals(group.transactions, currencyOf)
  return groups
}

function dayTotals(
  transactions: readonly Transaction[],
  currencyOf: (walletId: number) => string | undefined,
): CurrencyTotal[] {
  const amountsByCurrency = new Map<string, string[]>()
  for (const transaction of transactions) {
    const currency = currencyOf(transaction.wallet_id)
    if (transaction.is_hidden || !currency) continue
    amountsByCurrency.set(currency, [...(amountsByCurrency.get(currency) ?? []), transaction.amount])
  }
  return [...amountsByCurrency].map(([currency, amounts]) => ({ currency, amount: sumAmounts(amounts) }))
}

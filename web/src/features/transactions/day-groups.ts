import { totalsByCurrency, type CurrencyTotal } from "@/lib/currency-totals"
import { localDayKey } from "@/lib/dates"
import type { Transaction } from "./api"

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
  return totalsByCurrency(
    transactions.flatMap((transaction) => {
      const currency = currencyOf(transaction.wallet_id)
      return transaction.is_hidden || !currency ? [] : [{ currency, amount: transaction.amount }]
    }),
  )
}

import { sumAmounts } from "./decimal"
import { formatMoney } from "./money"

/** An exact decimal amount in one currency. Amounts in different currencies are never added together. */
export type CurrencyTotal = { currency: string; amount: string }

/** The amounts summed per currency, in the order each currency first appears. */
export function totalsByCurrency(items: Iterable<CurrencyTotal>): CurrencyTotal[] {
  const amountsByCurrency = new Map<string, string[]>()
  for (const { currency, amount } of items) {
    amountsByCurrency.set(currency, [...(amountsByCurrency.get(currency) ?? []), amount])
  }
  return [...amountsByCurrency].map(([currency, amounts]) => ({ currency, amount: sumAmounts(amounts) }))
}

/** Totals side by side, one per currency: "€1,200.00 · $35.00". */
export function formatTotals(totals: readonly CurrencyTotal[], format = formatMoney): string {
  return totals.map((total) => format(total.amount, total.currency)).join(" · ")
}

import { sumAmounts } from "./decimal"

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

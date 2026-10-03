import { Fragment } from "react"

import type { CurrencyTotal } from "@/lib/currency-totals"
import { amountTone, formatMoney, formatSigned } from "@/lib/money"
import { cn } from "@/lib/utils"

// How each kind of amount reads: transactions show money in and out (signed, green or red);
// balances show what an account holds, in the normal text color
const AMOUNT_STYLES = {
  transaction: { format: formatSigned, tone: amountTone },
  balance: { format: formatMoney, tone: () => "" },
} as const

export type AmountKind = keyof typeof AMOUNT_STYLES

type AmountProps = {
  // Exact decimal string from the API, e.g. "-46.3000"
  value: string
  // Unknown only for the moment before accounts finish loading: the raw value shows meanwhile
  currency?: string
  kind?: AmountKind
  className?: string
}

/** An amount the way CREAM shows its kind: a transaction ("+€10.00" green, "-€4.00" red) or a balance. */
export function Amount({ value, currency, kind = "transaction", className }: AmountProps) {
  const { format, tone } = AMOUNT_STYLES[kind]
  return (
    <span className={cn("tabular-nums", tone(value), className)}>{currency ? format(value, currency) : value}</span>
  )
}

type AmountTotalsProps = {
  totals: readonly CurrencyTotal[]
  kind?: AmountKind
  className?: string
}

/** Totals side by side, one per currency (never added together): "+€1,200.00 · -$35.00". */
export function AmountTotals({ totals, kind, className }: AmountTotalsProps) {
  return (
    <span className={className}>
      {totals.map((total, index) => (
        <Fragment key={total.currency}>
          {index > 0 && " · "}
          <Amount value={total.amount} currency={total.currency} kind={kind} />
        </Fragment>
      ))}
    </span>
  )
}

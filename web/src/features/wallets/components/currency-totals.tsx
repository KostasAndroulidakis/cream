import { useQuery } from "@tanstack/react-query"

import { Amount } from "@/components/amount"
import { walletTotalsQueryOptions } from "../api"

/** The headline number: what you have, one line per currency (never converted or mixed). */
export function CurrencyTotals() {
  const { data: totals, isPending, isError } = useQuery(walletTotalsQueryOptions)

  if (isPending) return <div className="h-14 w-48 animate-pulse rounded-lg bg-muted" aria-label="Loading totals" />
  if (isError || totals.length === 0) return null

  return (
    <dl className="space-y-1">
      <dt className="text-sm text-muted-foreground">Total balance</dt>
      {totals.map(({ currency, balance }) => (
        <dd
          key={currency}
          className="text-[clamp(2.25rem,6vw,3.5rem)] leading-none font-semibold tracking-tight tabular-nums"
        >
          <Amount value={balance} currency={currency} kind="balance" />
        </dd>
      ))}
    </dl>
  )
}

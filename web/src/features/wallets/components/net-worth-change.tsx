import { ArrowDownRight, ArrowUpRight } from "lucide-react"

import { percentChange, subtractAmounts } from "@/lib/decimal"
import { amountTone, formatMoney } from "@/lib/money"
import { cn } from "@/lib/utils"

type NetWorthChangeProps = {
  // Net worth on the range's first and last day (exact decimal strings)
  from: string
  to: string
  currency: string
  // The range as people say it, e.g. "1 month"
  rangeLabel: string
}

/** "↗ €36,181.22 (30.7%) 1 month change": green up, red down, as Monarch shows it. */
export function NetWorthChange({ from, to, currency, rangeLabel }: NetWorthChangeProps) {
  const change = subtractAmounts(to, from)
  const percent = percentChange(from, to)
  const Arrow = change.startsWith("-") ? ArrowDownRight : ArrowUpRight

  return (
    <p className="flex flex-wrap items-center gap-x-2 text-base">
      <span className={cn("inline-flex items-center gap-1 font-medium tabular-nums", amountTone(change))}>
        <Arrow className="size-4" aria-hidden />
        {formatMoney(change.replace(/^-/, ""), currency)}
        {percent !== null && ` (${percent.replace(/^-/, "")}%)`}
      </span>
      <span className="text-muted-foreground">{rangeLabel} change</span>
    </p>
  )
}

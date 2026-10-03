import { useQuery } from "@tanstack/react-query"
import { ChevronDown, Info } from "lucide-react"

import { AmountTotals } from "@/components/amount"
import { ComingSoonButton } from "@/components/coming-soon-button"
import { Surface } from "@/components/surface"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { cn } from "@/lib/utils"
import { accountsSummaryQueryOptions, netWorthQueryOptions, type NetWorthRange } from "../api"
import { toCurrencyTotals } from "../grouping"
import { NET_WORTH_RANGES } from "../net-worth"
import { useNetWorthRange } from "../use-net-worth-range"
import { NetWorthChange } from "./net-worth-change"
import { NetWorthChart } from "./net-worth-chart"

const NET_WORTH_HINT = "What you own minus what you owe, across your accounts. Excluded balances don't count."
// Both chart controls share one height
const CONTROL_HEIGHT = "h-10"
const LABEL_CLASS = "flex items-center gap-1.5 text-sm font-medium tracking-[0.08em] text-muted-foreground uppercase"

// The chart's height while its data loads, so the card doesn't jump
function ChartSkeleton() {
  return <div className="h-[300px] animate-pulse rounded-lg bg-muted" aria-label="Loading chart" />
}

/** The top of the Accounts page: net worth, its change over the chosen range, and the chart of it. */
export function NetWorthCard() {
  const [range, setRange] = useNetWorthRange()
  const { data: summary, isPending } = useQuery(accountsSummaryQueryOptions)
  const { data: history, isPending: isChartPending } = useQuery(netWorthQueryOptions(range))
  // EUR only for now, so one series; accounts made earlier in other currencies keep their own
  const series = history?.series[0]
  const first = series?.points[0]
  const last = series?.points.at(-1)

  return (
    <Surface label="Net worth">
      <div className="space-y-4 px-6 py-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-1">
            <p className={LABEL_CLASS}>
              Net worth
              <Info className="size-3.5" aria-label={NET_WORTH_HINT}>
                <title>{NET_WORTH_HINT}</title>
              </Info>
            </p>
            {isPending ? (
              <div className="h-9 w-56 animate-pulse rounded-lg bg-muted" aria-label="Loading net worth" />
            ) : (
              <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <AmountTotals
                  totals={toCurrencyTotals(summary?.net_worth ?? [])}
                  kind="balance"
                  className="text-[1.875rem] leading-9 font-semibold tracking-tight"
                />
                {series && first && last && (
                  <NetWorthChange
                    from={first.balance}
                    to={last.balance}
                    currency={series.currency}
                    rangeLabel={NET_WORTH_RANGES[range]}
                  />
                )}
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <ComingSoonButton className={CONTROL_HEIGHT}>
              Net worth performance
              <ChevronDown aria-hidden />
            </ComingSoonButton>
            <Select
              items={NET_WORTH_RANGES}
              value={range}
              // The items are exactly the ranges
              onValueChange={(value) => setRange(value as NetWorthRange)}
            >
              <SelectTrigger aria-label="Chart period" className={cn("w-40", CONTROL_HEIGHT)}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(NET_WORTH_RANGES).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        {isChartPending && <ChartSkeleton />}
        {series && <NetWorthChart series={series} />}
      </div>
    </Surface>
  )
}

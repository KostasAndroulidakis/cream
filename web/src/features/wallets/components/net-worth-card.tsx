import { useQuery } from "@tanstack/react-query"
import { ChevronDown, Info } from "lucide-react"

import { AmountTotals } from "@/components/amount"
import { ComingSoonButton } from "@/components/coming-soon-button"
import { Surface } from "@/components/surface"
import { accountsSummaryQueryOptions } from "../api"
import { toCurrencyTotals } from "../grouping"

const NET_WORTH_HINT = "What you own minus what you owe, across your accounts. Excluded balances don't count."

/** The top of the Accounts page: net worth, with the chart's controls (the chart comes with balance history). */
export function NetWorthCard() {
  const { data: summary, isPending } = useQuery(accountsSummaryQueryOptions)

  return (
    <Surface label="Net worth">
      <div className="flex flex-wrap items-start justify-between gap-4 px-6 py-6">
        <div className="space-y-2">
          <p className="flex items-center gap-1.5 text-sm font-medium tracking-[0.08em] text-muted-foreground uppercase">
            Net worth
            <Info className="size-3.5" aria-label={NET_WORTH_HINT}>
              <title>{NET_WORTH_HINT}</title>
            </Info>
          </p>
          {isPending ? (
            <div className="h-9 w-56 animate-pulse rounded-lg bg-muted" aria-label="Loading net worth" />
          ) : (
            <AmountTotals
              totals={toCurrencyTotals(summary?.net_worth ?? [])}
              kind="balance"
              className="block text-[1.875rem] leading-9 font-semibold tracking-tight"
            />
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <ComingSoonButton>
            Net worth performance
            <ChevronDown aria-hidden />
          </ComingSoonButton>
          <ComingSoonButton>
            1 month
            <ChevronDown aria-hidden />
          </ComingSoonButton>
        </div>
      </div>
    </Surface>
  )
}

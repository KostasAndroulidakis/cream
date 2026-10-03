import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { Amount } from "@/components/amount"
import { ListSkeleton } from "@/components/list-skeleton"
import { SegmentedControl } from "@/components/segmented-control"
import { Surface } from "@/components/surface"
import { accountsSummaryQueryOptions } from "../api"
import { summarizeByClass, type SummaryPart, type SummarySection } from "../summary"
import { useAccountTypes } from "../use-account-types"

const VIEWS = { totals: "Totals", percent: "Percent" } as const
type SummaryView = keyof typeof VIEWS

const SKELETON_ROWS = 4
// One list row of the sections below
const ROW_HEIGHT = "h-5"

// A part's value in the chosen view: its balance, or its share of the section
function PartValue({ part, currency, view }: { part: SummaryPart; currency: string; view: SummaryView }) {
  if (view === "totals") return <Amount value={part.amount} currency={currency} kind="balance" />
  return <span className="tabular-nums">{part.percent ?? "0.0"}%</span>
}

/** One class (Assets or Liabilities): its total, a bar split by type, and the types listed with their color. */
type SummarySectionViewProps = { section: SummarySection; currency: string; view: SummaryView }

function SummarySectionView({ section, currency, view }: SummarySectionViewProps) {
  return (
    <div className="space-y-3 px-6 py-5">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-semibold">{section.label}</h3>
        <Amount value={section.total} currency={currency} kind="balance" className="font-semibold" />
      </div>
      {/* Decorative: the list below carries the same numbers */}
      <div className="flex h-2 gap-0.5 overflow-hidden rounded-full bg-muted" aria-hidden>
        {section.parts.map((part) => (
          <span key={part.label} style={{ width: `${part.percent ?? 0}%`, backgroundColor: part.color }} />
        ))}
      </div>
      <ul className="space-y-2 text-sm">
        {section.parts.map((part) => (
          <li key={part.label} className="flex items-center gap-2">
            <span className="size-2 shrink-0 rounded-full" style={{ backgroundColor: part.color }} aria-hidden />
            <span className="flex-1 text-muted-foreground">{part.label}</span>
            <PartValue part={part} currency={currency} view={view} />
          </li>
        ))}
      </ul>
    </div>
  )
}

/** The Accounts page's side card: what you own and what you owe, by type, as totals or percents. */
export function SummaryCard() {
  const [view, setView] = useState<SummaryView>("totals")
  const { data: summary, isPending } = useQuery(accountsSummaryQueryOptions)
  const { catalog } = useAccountTypes()
  // EUR only for now: the summary's currency is net worth's (one, unless old accounts kept another)
  const currency = summary?.net_worth[0]?.currency
  const sections = summary && currency ? summarizeByClass(summary, catalog, currency) : []

  return (
    <Surface label="Summary">
      <div className="flex items-center justify-between gap-4 border-b px-6 py-4">
        <h2 className="text-lg font-semibold tracking-tight">Summary</h2>
        <SegmentedControl label="Show as" options={VIEWS} value={view} onChange={setView} />
      </div>
      {isPending ? (
        <div className="px-6">
          <ListSkeleton rows={SKELETON_ROWS} label="Loading summary" rowClassName={ROW_HEIGHT} />
        </div>
      ) : (
        <div className="divide-y">
          {currency &&
            sections.map((section) => (
              <SummarySectionView key={section.accountClass} section={section} currency={currency} view={view} />
            ))}
        </div>
      )}
    </Surface>
  )
}

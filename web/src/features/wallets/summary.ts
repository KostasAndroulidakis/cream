import { percentOf, sumAmounts } from "@/lib/decimal"
import { seriesColor } from "@/lib/series-colors"
import type { AccountClass, AccountTypeInfo, AccountsSummary } from "./api"

const CLASS_LABELS: Record<AccountClass, string> = { asset: "Assets", liability: "Liabilities" }
const CLASS_ORDER: readonly AccountClass[] = ["asset", "liability"]

export type SummaryPart = {
  label: string
  amount: string
  // Share of the section's total by size ("62.5"), null when the total is zero
  percent: string | null
  color: string
}

export type SummarySection = {
  accountClass: AccountClass
  label: string
  total: string
  parts: SummaryPart[]
}

/**
 * Assets and liabilities, each split by account type, in one currency.
 * A type's color follows its place in the catalog, so it stays the same whichever types you have.
 * Sections without accounts are left out.
 */
export function summarizeByClass(
  summary: AccountsSummary,
  catalog: readonly AccountTypeInfo[],
  currency: string,
): SummarySection[] {
  const amountByType = new Map(
    summary.types.map((total) => [total.type, total.totals.find((each) => each.currency === currency)?.balance]),
  )

  return CLASS_ORDER.map((accountClass) => {
    const parts = catalog
      .filter((info) => info.account_class === accountClass)
      .map((info, index) => ({ info, amount: amountByType.get(info.type), color: seriesColor(index) }))
      .filter((part): part is typeof part & { amount: string } => part.amount !== undefined)
    const total = sumAmounts(parts.map((part) => part.amount))
    return {
      accountClass,
      label: CLASS_LABELS[accountClass],
      total,
      parts: parts.map(({ info, amount, color }) => ({
        label: info.label,
        amount,
        percent: percentOf(amount, total),
        color,
      })),
    }
  }).filter((section) => section.parts.length > 0)
}

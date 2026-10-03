import type { SummaryRow } from "@/components/confirm-dialog"
import { NO_CATEGORY } from "@/features/categories/grouping"
import { tidyMerchantName } from "@/features/merchants/choices"
import { dateInputToISO, formatLongDate, localDayKey } from "@/lib/dates"
import type { Notice } from "@/lib/notify"
import { pluralize } from "@/lib/text"
import type { BulkChanges } from "./api"

/** The value of a bulk-edit field the user hasn't touched. */
export const NO_CHANGE = ""

/** Field names, shared by the form and the "Does this look right?" summary. */
export const BULK_FIELD_LABELS = {
  merchant: "Merchant",
  category: "Category",
  date: "Date",
  notes: "Notes",
  visibility: "Hide transactions",
} as const

/** "Hide transactions" choices and what each sets. */
export const VISIBILITY_CHOICES = {
  hide: { label: "Hide", isHidden: true },
  show: { label: "Show", isHidden: false },
} as const

export type VisibilityChoice = keyof typeof VISIBILITY_CHOICES

/** What the user has picked in the bulk-edit panel, as the form holds it. */
export type BulkEditDraft = {
  merchantName: string
  categoryId: string
  // YYYY-MM-DD from the date input
  date: string
  notes: string
  visibility: VisibilityChoice | typeof NO_CHANGE
}

export const EMPTY_DRAFT: BulkEditDraft = {
  merchantName: NO_CHANGE,
  categoryId: NO_CATEGORY,
  date: NO_CHANGE,
  notes: NO_CHANGE,
  visibility: NO_CHANGE,
}

/** The changes to send: only the fields the user changed. The one place that decides what changed. */
export function draftToChanges(draft: BulkEditDraft): BulkChanges {
  const changes: BulkChanges = {}
  const merchantName = tidyMerchantName(draft.merchantName)
  if (merchantName !== NO_CHANGE) changes.merchant_name = merchantName
  if (draft.categoryId !== NO_CATEGORY) changes.category_id = Number(draft.categoryId)
  if (draft.date !== NO_CHANGE) changes.occurred_at = dateInputToISO(draft.date)
  if (draft.notes.trim() !== NO_CHANGE) changes.description = draft.notes.trim()
  if (draft.visibility !== NO_CHANGE) changes.is_hidden = VISIBILITY_CHOICES[draft.visibility].isHidden
  return changes
}

export function hasChanges(changes: BulkChanges): boolean {
  return Object.keys(changes).length > 0
}

/** The changes as "field: new value" rows, for the user to confirm before applying them. */
export function summarizeChanges(
  changes: BulkChanges,
  categoryName: (categoryId: number) => string,
): SummaryRow[] {
  const rows: SummaryRow[] = []
  if (changes.merchant_name != null) {
    rows.push({ label: BULK_FIELD_LABELS.merchant, value: changes.merchant_name })
  }
  if (changes.category_id != null) {
    rows.push({ label: BULK_FIELD_LABELS.category, value: categoryName(changes.category_id) })
  }
  if (changes.occurred_at != null) {
    rows.push({ label: BULK_FIELD_LABELS.date, value: formatLongDate(localDayKey(changes.occurred_at)) })
  }
  if (changes.description != null) {
    rows.push({ label: BULK_FIELD_LABELS.notes, value: changes.description })
  }
  if (changes.is_hidden != null) {
    const choice = Object.values(VISIBILITY_CHOICES).find(({ isHidden }) => isHidden === changes.is_hidden)
    rows.push({ label: BULK_FIELD_LABELS.visibility, value: choice?.label ?? "" })
  }
  return rows
}

// "1 transaction was deleted." / "3 transactions were affected."
function affectedSentence(count: number, verb: string): string {
  return `${pluralize(count, "transaction")} ${count === 1 ? "was" : "were"} ${verb}.`
}

/** The notification after a bulk edit, counting what the API actually changed. */
export function bulkUpdateNotice(affected: number): Notice {
  return { title: "Transactions updated successfully", description: affectedSentence(affected, "affected") }
}

/** The notification after a bulk delete, counting what the API actually deleted. */
export function bulkDeleteNotice(affected: number): Notice {
  return { title: "Transactions deleted successfully", description: affectedSentence(affected, "deleted") }
}

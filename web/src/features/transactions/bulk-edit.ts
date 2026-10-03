import type { SummaryRow } from "@/components/confirm-changes-dialog"
import { NO_CATEGORY } from "@/features/categories/grouping"
import { dateInputToISO, formatLongDate, localDayKey } from "@/lib/dates"
import { pluralize } from "@/lib/text"
import type { BulkChanges } from "./api"

/** The value of a bulk-edit field the user hasn't touched. */
export const NO_CHANGE = ""

/** Field names, shared by the form and the "Does this look right?" summary. */
export const BULK_FIELD_LABELS = {
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
  categoryId: string
  // YYYY-MM-DD from the date input
  date: string
  notes: string
  visibility: VisibilityChoice | typeof NO_CHANGE
}

export const EMPTY_DRAFT: BulkEditDraft = {
  categoryId: NO_CATEGORY,
  date: NO_CHANGE,
  notes: NO_CHANGE,
  visibility: NO_CHANGE,
}

/** The changes to send: only the fields the user changed. The one place that decides what changed. */
export function draftToChanges(draft: BulkEditDraft): BulkChanges {
  const changes: BulkChanges = {}
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

/** The notification after a bulk edit, counting what the API actually changed. */
export function bulkUpdateNotice(affected: number): { title: string; description: string } {
  return {
    title: "Transactions updated successfully",
    description: `${pluralize(affected, "transaction")} ${affected === 1 ? "was" : "were"} affected.`,
  }
}

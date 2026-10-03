import { NO_CATEGORY } from "@/features/categories/grouping"
import { dateInputToISO } from "@/lib/dates"
import type { BulkChanges } from "./api"

/** The value of a bulk-edit field the user hasn't touched. */
export const NO_CHANGE = ""

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

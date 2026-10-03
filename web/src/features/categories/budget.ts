import type { BudgetBy } from "./api"

/** Monarch's choices for how a group is budgeted, "By category" first (the default). */
export const BUDGET_CHOICES: readonly { value: BudgetBy; label: string; hint: string }[] = [
  { value: "category", label: "By category", hint: "Budget by individual categories within this group." },
  { value: "group", label: "By group", hint: "Budget for the group as a whole, instead of each category." },
]

export const DEFAULT_BUDGET_BY: BudgetBy = "category"

export function budgetHint(value: BudgetBy): string {
  return BUDGET_CHOICES.find((choice) => choice.value === value)?.hint ?? ""
}

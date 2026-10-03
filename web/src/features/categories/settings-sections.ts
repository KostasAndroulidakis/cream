import type { Category, CategoryType } from "./api"

export type CategoryGroupBlock = {
  // null for the user's categories that sit in no group
  group: Category | null
  categories: Category[]
}

export type CategorySection = { type: CategoryType; title: string; groups: CategoryGroupBlock[] }

// Monarch's order and names for the three kinds
const SECTIONS: readonly { type: CategoryType; title: string }[] = [
  { type: "income", title: "Income" },
  { type: "expense", title: "Expenses" },
  { type: "transfer", title: "Transfers" },
]

/** Settings › Categories: each kind, its groups in API order, each group's categories in the user's order. */
export function categorySections(categories: Category[]): CategorySection[] {
  return SECTIONS.map(({ type, title }) => {
    const ofType = categories.filter((category) => category.type === type)
    const groups: CategoryGroupBlock[] = ofType
      .filter((category) => category.is_group)
      .map((group) => ({
        group,
        categories: ofType.filter((category) => !category.is_group && category.parent_id === group.id),
      }))
    const ungrouped = ofType.filter((category) => !category.is_group && category.parent_id === null)
    if (ungrouped.length > 0) groups.push({ group: null, categories: ungrouped })
    return { type, title, groups }
  })
}

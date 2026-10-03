import type { Category, CategoryType } from "./api"

export type CategoryGroup = { label: string; categories: Category[] }

const UNGROUPED_LABEL = "My categories"

/** Value of a category picker before anything is picked. */
export const NO_CATEGORY = ""

/** Every category type, most used first, for pickers that aren't tied to one kind of transaction. */
export const ALL_CATEGORY_TYPES: readonly CategoryType[] = ["expense", "income", "transfer"]

/** Categories by ID, for showing names next to transactions and rules. */
export function categoriesById(categories: Category[]): Map<number, Category> {
  return new Map(categories.map((category) => [category.id, category]))
}

/**
 * Categories a transaction can use, organized under their groups. Groups follow the order of
 * `types` (most likely first), then API order. Groups themselves are never selectable;
 * top-level user categories go under "My categories".
 */
export function groupAssignableCategories(categories: Category[], types: readonly CategoryType[]): CategoryGroup[] {
  const groups = new Map<string, CategoryGroup & { type: CategoryType }>()
  const byId = categoriesById(categories)

  for (const category of categories) {
    if (category.is_group || !types.includes(category.type)) continue
    const parent = category.parent_id === null ? undefined : byId.get(category.parent_id)
    const groupKey = `${category.type}:${parent?.id ?? UNGROUPED_LABEL}`
    const group = groups.get(groupKey) ?? { label: parent?.name ?? UNGROUPED_LABEL, type: category.type, categories: [] }
    group.categories.push(category)
    groups.set(groupKey, group)
  }
  return [...groups.values()]
    .sort((a, b) => types.indexOf(a.type) - types.indexOf(b.type))
    .map(({ label, categories }) => ({ label, categories }))
}

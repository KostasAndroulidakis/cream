import type { Category, CategoryType } from "./api"

export type CategoryGroup = { label: string; categories: Category[] }

const UNGROUPED_LABEL = "My categories"

/**
 * Categories a transaction can use, organized under their groups (in API order).
 * Groups themselves are never selectable; top-level user categories go under "My categories".
 */
export function groupAssignableCategories(categories: Category[], type: CategoryType): CategoryGroup[] {
  const groups = new Map<number | null, CategoryGroup>()
  const byId = new Map(categories.map((category) => [category.id, category]))

  for (const category of categories) {
    if (category.is_group || category.type !== type) continue
    const parent = category.parent_id === null ? undefined : byId.get(category.parent_id)
    const groupId = parent?.id ?? null
    const group = groups.get(groupId) ?? { label: parent?.name ?? UNGROUPED_LABEL, categories: [] }
    group.categories.push(category)
    groups.set(groupId, group)
  }
  return [...groups.values()]
}

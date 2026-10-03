import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"
import { RULES_KEY } from "@/features/categorization/api"

export type Category = Schemas["CategoryRead"]
export type CategoryType = Schemas["CategoryType"]
export type BudgetBy = Schemas["BudgetBy"]
export type CategoryCreateInput = Schemas["CategoryCreate"]
export type CategoryUpdateInput = Schemas["CategoryUpdate"]

export const categoriesQueryOptions = queryOptions({
  queryKey: ["categories"],
  queryFn: async (): Promise<Category[]> => {
    const { data, error, response } = await api.GET("/api/v1/categories")
    if (!data) throw toApiError(error, response)
    return data
  },
})

async function reorderCategories(categoryIds: number[]): Promise<void> {
  const { error, response } = await api.PUT("/api/v1/categories/order", { body: { category_ids: categoryIds } })
  if (!response.ok) throw toApiError(error, response)
}

/** The given IDs in this order, everything else where it was. */
function applyOrder(categories: Category[], categoryIds: number[]): Category[] {
  const moved = new Set(categoryIds)
  const byId = new Map(categories.map((category) => [category.id, category]))
  const inOrder = categoryIds.map((id) => byId.get(id)).filter((category) => category !== undefined)
  // The group's slots in the list stay the same; they're filled in the new order
  let next = 0
  return categories.map((category) => (moved.has(category.id) ? inOrder[next++] : category))
}

/**
 * Saves one group's new order. The list shows it at once (a drop must not jump back while the
 * request runs) and returns to the saved order if the API refuses it.
 */
export function useReorderCategories() {
  const queryClient = useQueryClient()
  const { queryKey } = categoriesQueryOptions

  return useMutation({
    mutationFn: reorderCategories,
    onMutate: async (categoryIds) => {
      await queryClient.cancelQueries({ queryKey })
      const previous = queryClient.getQueryData(queryKey)
      if (previous) queryClient.setQueryData(queryKey, applyOrder(previous, categoryIds))
      return { previous }
    },
    onError: (_error, _ids, context) => {
      if (context?.previous) queryClient.setQueryData(queryKey, context.previous)
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey }),
  })
}

async function createCategory(input: CategoryCreateInput): Promise<Category> {
  const { data, error, response } = await api.POST("/api/v1/categories", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

async function updateCategory({ id, changes }: { id: number; changes: CategoryUpdateInput }): Promise<Category> {
  const { data, error, response } = await api.PATCH("/api/v1/categories/{category_id}", {
    params: { path: { category_id: id } },
    body: changes,
  })
  if (!data) throw toApiError(error, response)
  return data
}

async function deleteCategory(id: number): Promise<void> {
  const { error, response } = await api.DELETE("/api/v1/categories/{category_id}", {
    params: { path: { category_id: id } },
  })
  if (!response.ok) throw toApiError(error, response)
}

function useCategoryMutation<TInput, TResult>(mutationFn: (input: TInput) => Promise<TResult>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn,
    // Deleting can also remove merchant rules that pointed at the deleted categories
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: categoriesQueryOptions.queryKey }),
        queryClient.invalidateQueries({ queryKey: RULES_KEY }),
      ]),
  })
}

export function useCreateCategory() {
  return useCategoryMutation(createCategory)
}

export function useUpdateCategory() {
  return useCategoryMutation(updateCategory)
}

export function useDeleteCategory() {
  return useCategoryMutation(deleteCategory)
}

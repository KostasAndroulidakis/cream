import { queryOptions } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Category = Schemas["CategoryRead"]
export type CategoryType = Schemas["CategoryType"]

export const categoriesQueryOptions = queryOptions({
  queryKey: ["categories"],
  queryFn: async (): Promise<Category[]> => {
    const { data, error, response } = await api.GET("/api/v1/categories")
    if (!data) throw toApiError(error, response)
    return data
  },
})

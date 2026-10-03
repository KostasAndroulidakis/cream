import { queryOptions } from "@tanstack/react-query"

import { TRANSACTIONS_KEY } from "@/features/transactions/api"
import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Merchant = Schemas["MerchantRead"]

/** The user's merchants that have transactions, by name. */
export const merchantsQueryOptions = queryOptions({
  // Derived from the transactions, so it refreshes whenever they do
  queryKey: [...TRANSACTIONS_KEY, "merchants"],
  queryFn: async (): Promise<Merchant[]> => {
    const { data, error, response } = await api.GET("/api/v1/merchants")
    if (!data) throw toApiError(error, response)
    return data
  },
})

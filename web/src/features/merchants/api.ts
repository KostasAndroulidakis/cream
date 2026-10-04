import { queryOptions } from "@tanstack/react-query"

import { TRANSACTIONS_KEY } from "@/features/transactions/api"
import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Merchant = Schemas["MerchantRead"]
export type MerchantSummary = Schemas["MerchantSummary"]
export type MerchantOrder = Schemas["MerchantOrder"]

/** The user's merchants that have transactions, with their counts: most used first, or by name. */
export function merchantsQueryOptions(order: MerchantOrder) {
  return queryOptions({
    // Derived from the transactions, so it refreshes whenever they do
    queryKey: [...TRANSACTIONS_KEY, "merchants", order],
    queryFn: async (): Promise<MerchantSummary[]> => {
      const { data, error, response } = await api.GET("/api/v1/merchants", { params: { query: { order } } })
      if (!data) throw toApiError(error, response)
      return data
    },
  })
}

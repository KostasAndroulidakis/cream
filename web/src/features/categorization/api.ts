import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { TRANSACTIONS_KEY } from "@/features/transactions/api"
import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type TransactionPage = Schemas["TransactionPage"]
export type MerchantRule = Schemas["MerchantRuleRead"]
export type CategorizeResult = Schemas["CategorizeResultRead"]

// The inbox shows the newest transactions that need review; the rest appear as these get reviewed
const INBOX_PAGE_SIZE = 50
export const RULES_KEY = ["rules"] as const

/** Under the transactions prefix, so imports and edits refresh the inbox too. */
export const inboxQueryOptions = queryOptions({
  queryKey: [...TRANSACTIONS_KEY, "needs-review", INBOX_PAGE_SIZE],
  queryFn: async (): Promise<TransactionPage> => {
    const { data, error, response } = await api.GET("/api/v1/transactions/needs-review", {
      params: { query: { limit: INBOX_PAGE_SIZE } },
    })
    if (!data) throw toApiError(error, response)
    return data
  },
})

export const rulesQueryOptions = queryOptions({
  queryKey: RULES_KEY,
  queryFn: async (): Promise<MerchantRule[]> => {
    const { data, error, response } = await api.GET("/api/v1/rules")
    if (!data) throw toApiError(error, response)
    return data
  },
})

export type CategorizeInput = {
  transactionId: number
  categoryId: number
  // Also remember it for the merchant: its other transactions and future imports
  applyToSimilar: boolean
}

export function useCategorizeTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ transactionId, categoryId, applyToSimilar }: CategorizeInput): Promise<CategorizeResult> => {
      const { data, error, response } = await api.POST("/api/v1/transactions/{transaction_id}/categorize", {
        params: { path: { transaction_id: transactionId } },
        body: { category_id: categoryId, apply_to_similar: applyToSimilar },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
        queryClient.invalidateQueries({ queryKey: RULES_KEY }),
      ]),
  })
}

export function useDeleteRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (ruleId: number) => {
      const { error, response } = await api.DELETE("/api/v1/rules/{rule_id}", {
        params: { path: { rule_id: ruleId } },
      })
      if (!response.ok) throw toApiError(error, response)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: RULES_KEY }),
  })
}

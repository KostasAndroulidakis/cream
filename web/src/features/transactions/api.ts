import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"
import { WALLETS_KEY } from "@/features/wallets/api"

export type Transaction = Schemas["TransactionRead"]
export type TransactionCreateInput = Schemas["TransactionCreate"]

// Every transaction query lives under this prefix so one invalidation refreshes them all
export const TRANSACTIONS_KEY = ["transactions"] as const

export function recentTransactionsQueryOptions(limit: number) {
  return queryOptions({
    queryKey: [...TRANSACTIONS_KEY, "recent", limit],
    queryFn: async (): Promise<Transaction[]> => {
      const { data, error, response } = await api.GET("/api/v1/transactions", { params: { query: { limit } } })
      if (!data) throw toApiError(error, response)
      return data
    },
  })
}

async function createTransaction(input: TransactionCreateInput): Promise<Transaction> {
  const { data, error, response } = await api.POST("/api/v1/transactions", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createTransaction,
    // Balances and totals depend on transactions, so they refresh together
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
        queryClient.invalidateQueries({ queryKey: WALLETS_KEY }),
      ]),
  })
}

export type SetHiddenInput = { transactionId: number; hidden: boolean }

/** Hide a transaction from lists and statistics, or show it again. */
export function useSetTransactionHidden() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ transactionId, hidden }: SetHiddenInput): Promise<Transaction> => {
      const { data, error, response } = await api.PATCH("/api/v1/transactions/{transaction_id}", {
        params: { path: { transaction_id: transactionId } },
        body: { is_hidden: hidden },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
    // Hidden transactions still count in balances, so only transaction lists need refreshing
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
  })
}

import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Transaction = Schemas["TransactionRead"]
export type TransactionCreateInput = Schemas["TransactionCreate"]

const TRANSACTIONS_KEY = ["transactions"] as const
// Balances and totals depend on transactions, so they refresh together
const WALLETS_KEY = ["wallets"] as const

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
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
        queryClient.invalidateQueries({ queryKey: WALLETS_KEY }),
      ]),
  })
}

import { infiniteQueryOptions, queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"
import { WALLETS_KEY } from "@/features/wallets/api"

export type Transaction = Schemas["TransactionRead"]
export type TransactionCreateInput = Schemas["TransactionCreate"]

// Every transaction query lives under this prefix so one invalidation refreshes them all
export const TRANSACTIONS_KEY = ["transactions"] as const

/** The newest transactions; hidden ones only when asked for. */
export function recentTransactionsQueryOptions(limit: number, includeHidden: boolean) {
  return queryOptions({
    queryKey: [...TRANSACTIONS_KEY, "recent", limit, { includeHidden }],
    queryFn: async (): Promise<Transaction[]> => {
      const { data, error, response } = await api.GET("/api/v1/transactions", {
        params: { query: { limit, include_hidden: includeHidden } },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
  })
}

// Transactions page: loaded a page at a time, newest first
const ALL_PAGE_SIZE = 100

export const allTransactionsQueryOptions = infiniteQueryOptions({
  queryKey: [...TRANSACTIONS_KEY, "all"],
  queryFn: async ({ pageParam }): Promise<Transaction[]> => {
    const { data, error, response } = await api.GET("/api/v1/transactions", {
      params: { query: { limit: ALL_PAGE_SIZE, offset: pageParam } },
    })
    if (!data) throw toApiError(error, response)
    return data
  },
  initialPageParam: 0,
  // A full page may have more after it; a short one is the end
  getNextPageParam: (lastPage, allPages) =>
    lastPage.length === ALL_PAGE_SIZE ? allPages.length * ALL_PAGE_SIZE : undefined,
})

async function createTransaction(input: TransactionCreateInput): Promise<Transaction> {
  const { data, error, response } = await api.POST("/api/v1/transactions", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

/** Refreshes transaction lists together with wallets, for changes that move balances. */
function useRefreshTransactionsAndBalances() {
  const queryClient = useQueryClient()
  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY }),
      queryClient.invalidateQueries({ queryKey: WALLETS_KEY }),
    ])
}

export function useCreateTransaction() {
  return useMutation({ mutationFn: createTransaction, onSuccess: useRefreshTransactionsAndBalances() })
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

/** Delete a transaction entered by hand (the API refuses bank transactions: hide those instead). */
export function useDeleteTransaction() {
  return useMutation({
    mutationFn: async (transactionId: number) => {
      const { error, response } = await api.DELETE("/api/v1/transactions/{transaction_id}", {
        params: { path: { transaction_id: transactionId } },
      })
      if (!response.ok) throw toApiError(error, response)
    },
    onSuccess: useRefreshTransactionsAndBalances(),
  })
}

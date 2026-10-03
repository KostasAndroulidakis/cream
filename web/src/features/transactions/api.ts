import { infiniteQueryOptions, queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"
import { WALLETS_KEY } from "@/features/wallets/api"

export type Transaction = Schemas["TransactionRead"]
export type TransactionCreateInput = Schemas["TransactionCreate"]
export type BulkChanges = Schemas["BulkTransactionChanges"]
export type BulkResult = Schemas["BulkResult"]

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

/** One page of a transactions list; `total` only where the API counts the whole list. */
export type TransactionsPage = { items: Transaction[]; total?: number }

// Transactions page: loaded a page at a time, newest first
const LIST_PAGE_SIZE = 100

/** A list loaded a page at a time; `fetchPage` gets one page of it from the API. */
function pagedTransactionsQueryOptions(
  name: string,
  fetchPage: (limit: number, offset: number) => Promise<TransactionsPage>,
) {
  return infiniteQueryOptions({
    queryKey: [...TRANSACTIONS_KEY, "pages", name],
    queryFn: ({ pageParam }) => fetchPage(LIST_PAGE_SIZE, pageParam),
    initialPageParam: 0,
    // A full page may have more after it; a short one is the end
    getNextPageParam: (lastPage, allPages) =>
      lastPage.items.length === LIST_PAGE_SIZE ? allPages.length * LIST_PAGE_SIZE : undefined,
  })
}

/** Every visible transaction. */
export const allTransactionsQueryOptions = pagedTransactionsQueryOptions("all", async (limit, offset) => {
  const { data, error, response } = await api.GET("/api/v1/transactions", {
    params: { query: { limit, offset } },
  })
  if (!data) throw toApiError(error, response)
  return { items: data }
})

/** The review inbox: visible transactions that need review, with their total count. */
export const needsReviewTransactionsQueryOptions = pagedTransactionsQueryOptions(
  "needs-review",
  async (limit, offset) => {
    const { data, error, response } = await api.GET("/api/v1/transactions/needs-review", {
      params: { query: { limit, offset } },
    })
    if (!data) throw toApiError(error, response)
    return data
  },
)

async function createTransaction(input: TransactionCreateInput): Promise<Transaction> {
  const { data, error, response } = await api.POST("/api/v1/transactions", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

/** Refreshes every transaction list, for changes that leave balances as they are. */
function useRefreshTransactions() {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY })
}

/** Refreshes transaction lists together with wallets, for changes that move balances. */
function useRefreshTransactionsAndBalances() {
  const queryClient = useQueryClient()
  const refreshTransactions = useRefreshTransactions()
  return () => Promise.all([refreshTransactions(), queryClient.invalidateQueries({ queryKey: WALLETS_KEY })])
}

export function useCreateTransaction() {
  return useMutation({ mutationFn: createTransaction, onSuccess: useRefreshTransactionsAndBalances() })
}

export type SetHiddenInput = { transactionId: number; hidden: boolean }

/** Hide a transaction from lists and statistics, or show it again. */
export function useSetTransactionHidden() {
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
    onSuccess: useRefreshTransactions(),
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

export type BulkUpdateInput = { transactionIds: number[]; changes: BulkChanges }

/** The same changes on several transactions: all of them, or none if the API refuses any. */
export function useBulkUpdateTransactions() {
  return useMutation({
    mutationFn: async ({ transactionIds, changes }: BulkUpdateInput): Promise<BulkResult> => {
      const { data, error, response } = await api.POST("/api/v1/transactions/bulk-update", {
        body: { transaction_ids: transactionIds, changes },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
    // Category, notes, hiding and the dates of hand-entered transactions don't move balances
    onSuccess: useRefreshTransactions(),
  })
}

/** Delete several transactions entered by hand: all of them, or none if any came from a bank. */
export function useBulkDeleteTransactions() {
  return useMutation({
    mutationFn: async (transactionIds: number[]): Promise<BulkResult> => {
      const { data, error, response } = await api.POST("/api/v1/transactions/bulk-delete", {
        body: { transaction_ids: transactionIds },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: useRefreshTransactionsAndBalances(),
  })
}

/** Mark every transaction in the review inbox reviewed. */
export function useMarkAllReviewed() {
  return useMutation({
    mutationFn: async (): Promise<BulkResult> => {
      const { data, error, response } = await api.POST("/api/v1/transactions/needs-review/mark-all-reviewed")
      if (!data) throw toApiError(error, response)
      return data
    },
    // Reviewing doesn't move balances
    onSuccess: useRefreshTransactions(),
  })
}

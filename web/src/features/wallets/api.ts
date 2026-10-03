import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Wallet = Schemas["WalletRead"]
export type WalletType = Schemas["WalletType"]
export type WalletCreateInput = Schemas["WalletCreate"]
export type WalletUpdateInput = Schemas["WalletUpdate"]
export type CurrencyTotal = Schemas["CurrencyTotal"]
export type AccountTypeInfo = Schemas["AccountTypeRead"]
export type AccountClass = Schemas["AccountClass"]
export type AccountsSummary = Schemas["AccountsSummary"]
export type TypeTotal = Schemas["TypeTotal"]
export type NetWorthRange = Schemas["NetWorthRange"]
export type NetWorthHistory = Schemas["NetWorthHistory"]

// Every wallet query lives under this prefix so one invalidation refreshes them all
export const WALLETS_KEY = ["wallets"] as const

export const walletsQueryOptions = queryOptions({
  queryKey: [...WALLETS_KEY, "list"],
  queryFn: async (): Promise<Wallet[]> => {
    const { data, error, response } = await api.GET("/api/v1/wallets")
    if (!data) throw toApiError(error, response)
    return data
  },
})

/** What an account can be: types and subtypes, in Monarch's order. Fixed in the API, so loaded once. */
export const accountTypesQueryOptions = queryOptions({
  queryKey: [...WALLETS_KEY, "types"],
  queryFn: async (): Promise<AccountTypeInfo[]> => {
    const { data, error, response } = await api.GET("/api/v1/wallets/types")
    if (!data) throw toApiError(error, response)
    return data
  },
  staleTime: Infinity,
})

/** Net worth and each type's total, counted by the API's one rule (excluded balances left out). */
export const accountsSummaryQueryOptions = queryOptions({
  queryKey: [...WALLETS_KEY, "summary"],
  queryFn: async (): Promise<AccountsSummary> => {
    const { data, error, response } = await api.GET("/api/v1/wallets/summary")
    if (!data) throw toApiError(error, response)
    return data
  },
})

/** Net worth day by day over a range, for the Accounts chart. */
export function netWorthQueryOptions(range: NetWorthRange) {
  return queryOptions({
    queryKey: [...WALLETS_KEY, "net-worth", range],
    queryFn: async (): Promise<NetWorthHistory> => {
      const { data, error, response } = await api.GET("/api/v1/wallets/net-worth", {
        params: { query: { range } },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
  })
}

export const walletTotalsQueryOptions = queryOptions({
  queryKey: [...WALLETS_KEY, "totals"],
  queryFn: async (): Promise<CurrencyTotal[]> => {
    const { data, error, response } = await api.GET("/api/v1/wallets/totals")
    if (!data) throw toApiError(error, response)
    return data
  },
})

async function createWallet(input: WalletCreateInput): Promise<Wallet> {
  const { data, error, response } = await api.POST("/api/v1/wallets", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

export function useCreateWallet() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createWallet,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: WALLETS_KEY }),
  })
}

async function updateWallet({ id, changes }: { id: number; changes: WalletUpdateInput }): Promise<Wallet> {
  const { data, error, response } = await api.PATCH("/api/v1/wallets/{wallet_id}", {
    params: { path: { wallet_id: id } },
    body: changes,
  })
  if (!data) throw toApiError(error, response)
  return data
}

async function deleteWallet(id: number): Promise<void> {
  const { error, response } = await api.DELETE("/api/v1/wallets/{wallet_id}", { params: { path: { wallet_id: id } } })
  if (!response.ok) throw toApiError(error, response)
}

// An account's settings reach far: balances, totals, which transactions show, its bank link
function useInvalidateEverything() {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries()
}

/** Edit Account: name, balance, type, credit limit and the balance and visibility switches. */
export function useUpdateWallet() {
  const invalidate = useInvalidateEverything()
  return useMutation({ mutationFn: updateWallet, onSuccess: invalidate })
}

/** Delete account: the account and all its transactions. */
export function useDeleteWallet() {
  const invalidate = useInvalidateEverything()
  return useMutation({ mutationFn: deleteWallet, onSuccess: invalidate })
}

import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"

export type Wallet = Schemas["WalletRead"]
export type WalletType = Schemas["WalletType"]
export type WalletCreateInput = Schemas["WalletCreate"]
export type CurrencyTotal = Schemas["CurrencyTotal"]

// Every wallet query lives under this prefix so one invalidation refreshes them all
const WALLETS_KEY = ["wallets"] as const

export const walletsQueryOptions = queryOptions({
  queryKey: [...WALLETS_KEY, "list"],
  queryFn: async (): Promise<Wallet[]> => {
    const { data, error, response } = await api.GET("/api/v1/wallets")
    if (!data) throw toApiError(error, response)
    return data
  },
})

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

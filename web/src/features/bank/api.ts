import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import type { Schemas } from "@/lib/api/types"
import { TRANSACTIONS_KEY } from "@/features/transactions/api"
import { WALLETS_KEY } from "@/features/wallets/api"

export type Aspsp = Schemas["AspspRead"]
export type BankConnection = Schemas["BankConnectionRead"]
export type BankAccount = Schemas["BankAccountRead"]
export type SyncResult = Schemas["SyncResultRead"]

const BANK_KEY = ["bank"] as const
// A sync or a new link changes wallets and transactions too
const DEPENDENT_KEYS = [WALLETS_KEY, TRANSACTIONS_KEY] as const

export function aspspsQueryOptions(country: string) {
  return queryOptions({
    queryKey: [...BANK_KEY, "aspsps", country],
    queryFn: async (): Promise<Aspsp[]> => {
      const { data, error, response } = await api.GET("/api/v1/bank/aspsps", { params: { query: { country } } })
      if (!data) throw toApiError(error, response)
      return data
    },
    // The list of banks rarely changes
    staleTime: Infinity,
  })
}

export const connectionsQueryOptions = queryOptions({
  queryKey: [...BANK_KEY, "connections"],
  queryFn: async (): Promise<BankConnection[]> => {
    const { data, error, response } = await api.GET("/api/v1/bank/connections")
    if (!data) throw toApiError(error, response)
    return data
  },
})

function useInvalidateBankData() {
  const queryClient = useQueryClient()
  return () =>
    Promise.all(
      [BANK_KEY, ...DEPENDENT_KEYS].map((queryKey) => queryClient.invalidateQueries({ queryKey })),
    )
}

/** Starts the bank login and leaves CREAM for the bank's page. */
export function useStartConnection() {
  return useMutation({
    mutationFn: async (input: Schemas["ConnectionStart"]) => {
      const { data, error, response } = await api.POST("/api/v1/bank/connections", { body: input })
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: ({ url }) => window.location.assign(url),
  })
}

export function useCompleteConnection() {
  const invalidate = useInvalidateBankData()
  return useMutation({
    mutationFn: async (input: Schemas["ConnectionComplete"]) => {
      const { data, error, response } = await api.POST("/api/v1/bank/connections/complete", { body: input })
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useLinkAccount() {
  const invalidate = useInvalidateBankData()
  return useMutation({
    mutationFn: async ({ accountId, walletId }: { accountId: number; walletId: number | null }) => {
      const { data, error, response } = await api.POST("/api/v1/bank/accounts/{account_id}/link", {
        params: { path: { account_id: accountId } },
        body: { wallet_id: walletId },
      })
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useSyncBanks() {
  const invalidate = useInvalidateBankData()
  return useMutation({
    mutationFn: async (): Promise<SyncResult[]> => {
      const { data, error, response } = await api.POST("/api/v1/bank/sync")
      if (!data) throw toApiError(error, response)
      return data
    },
    onSuccess: invalidate,
  })
}

export function useDeleteConnection() {
  const invalidate = useInvalidateBankData()
  return useMutation({
    mutationFn: async (connectionId: number) => {
      const { error, response } = await api.DELETE("/api/v1/bank/connections/{connection_id}", {
        params: { path: { connection_id: connectionId } },
      })
      if (!response.ok) throw toApiError(error, response)
    },
    onSuccess: invalidate,
  })
}

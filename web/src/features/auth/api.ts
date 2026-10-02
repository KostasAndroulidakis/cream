import { queryOptions, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import { toApiError } from "@/lib/api/errors"
import { HTTP_STATUS } from "@/lib/api/http-status"
import type { Schemas } from "@/lib/api/types"

export type User = Schemas["UserRead"]
export type LoginInput = Schemas["LoginRequest"]
export type SignupInput = Schemas["UserCreate"]

const CURRENT_USER_KEY = ["auth", "me"] as const

async function fetchCurrentUser(): Promise<User | null> {
  const { data, error, response } = await api.GET("/api/v1/auth/me")
  // No session is a normal state, not an error
  if (response.status === HTTP_STATUS.UNAUTHORIZED) return null
  if (!data) throw toApiError(error, response)
  return data
}

async function login(input: LoginInput): Promise<User> {
  const { data, error, response } = await api.POST("/api/v1/auth/login", { body: input })
  if (!data) throw toApiError(error, response)
  return data
}

async function signup(input: SignupInput): Promise<User> {
  const { data, error, response } = await api.POST("/api/v1/auth/signup", { body: input })
  if (!data) throw toApiError(error, response)
  // A new account starts signed in
  return login({ username: input.username, password: input.password })
}

async function logout(): Promise<void> {
  await api.POST("/api/v1/auth/logout")
}

export const currentUserQueryOptions = queryOptions({
  queryKey: CURRENT_USER_KEY,
  queryFn: fetchCurrentUser,
  retry: false,
})

export function useCurrentUser() {
  return useQuery(currentUserQueryOptions)
}

function useSessionMutation<TInput>(mutationFn: (input: TInput) => Promise<User>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn,
    onSuccess: (user) => queryClient.setQueryData(CURRENT_USER_KEY, user),
  })
}

export function useLogin() {
  return useSessionMutation(login)
}

export function useSignup() {
  return useSessionMutation(signup)
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      // Drop every cached piece of the previous user's data
      queryClient.clear()
      queryClient.setQueryData(CURRENT_USER_KEY, null)
    },
  })
}

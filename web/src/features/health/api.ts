import { queryOptions } from "@tanstack/react-query"

import { api } from "@/lib/api/client"
import type { Schemas } from "@/lib/api/types"

const HEALTH_POLL_INTERVAL_MS = 10_000

export type Health = Schemas["HealthResponse"]

function isHealth(value: unknown): value is Health {
  return typeof value === "object" && value !== null && "api" in value && "database" in value
}

async function fetchHealth(): Promise<Health> {
  const { data, error } = await api.GET("/api/v1/health")
  // A 503 still carries a HealthResponse body describing which dependency is down
  const body: unknown = data ?? error
  if (!isHealth(body)) {
    throw new Error("API unreachable")
  }
  return body
}

export const healthQueryOptions = queryOptions({
  queryKey: ["health"],
  queryFn: fetchHealth,
  refetchInterval: HEALTH_POLL_INTERVAL_MS,
  retry: false,
})

import type { Schemas } from "@/lib/api/types"
import type { Transaction } from "@/features/transactions/api"

type CategorySource = Schemas["CategorySource"]

// Chosen by a merchant rule or the bank's merchant category code, not by hand
const AUTOMATIC_SOURCES: readonly CategorySource[] = ["rule", "mcc"]

export function isAutoCategorized(transaction: Transaction): boolean {
  return AUTOMATIC_SOURCES.includes(transaction.category_source)
}

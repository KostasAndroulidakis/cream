import type { CategoryType } from "@/features/categories/api"
import { isMoneyIn } from "@/lib/amount"

// Most likely first. Money in can be a refund (an expense category); either way it can be a transfer.
const MONEY_IN_TYPES: readonly CategoryType[] = ["income", "transfer", "expense"]
const MONEY_OUT_TYPES: readonly CategoryType[] = ["expense", "transfer"]

/** Category types that make sense for a transaction of this amount, most likely first. */
export function categoryTypesFor(amount: string): readonly CategoryType[] {
  return isMoneyIn(amount) ? MONEY_IN_TYPES : MONEY_OUT_TYPES
}

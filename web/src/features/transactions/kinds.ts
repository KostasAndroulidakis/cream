import type { CategoryType } from "@/features/categories/api"

/** What a person records by hand. Transfers arrive later with bank sync and their own flow. */
export const TRANSACTION_KINDS = ["expense", "income"] as const satisfies readonly CategoryType[]
export type TransactionKind = (typeof TRANSACTION_KINDS)[number]

export const KIND_LABELS: Record<TransactionKind, string> = {
  expense: "Expense",
  income: "Income",
}

/** The API stores expenses as negative amounts and income as positive. */
export function signedAmount(amount: string, kind: TransactionKind): string {
  return kind === "expense" ? `-${amount}` : amount
}

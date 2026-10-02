import { z } from "zod"

import { amountInput, isZeroAmount } from "@/lib/amount"
import { todayInputValue } from "@/lib/dates"
import { TRANSACTION_KINDS } from "./kinds"

const DESCRIPTION_MAX = 200

export const createTransactionSchema = z.object({
  kind: z.enum(TRANSACTION_KINDS),
  amount: amountInput({ allowNegative: false }).refine((value) => !isZeroAmount(value), "Enter an amount above zero"),
  category_id: z.coerce.number<string>().int().positive("Pick a category"),
  wallet_id: z.coerce.number<string>().int().positive("Pick a wallet"),
  // ISO dates compare correctly as strings
  date: z.string().min(1, "Pick a date").refine((value) => value <= todayInputValue(), "The date can't be in the future"),
  description: z.string().trim().max(DESCRIPTION_MAX, `Use at most ${DESCRIPTION_MAX} characters`),
})

export type CreateTransactionFormInput = z.input<typeof createTransactionSchema>
export type CreateTransactionValues = z.output<typeof createTransactionSchema>

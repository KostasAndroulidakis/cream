import { z } from "zod"

import { amountInput } from "@/lib/amount"
import type { WalletCreateInput } from "./api"
import { WALLET_TYPES } from "./wallet-types"

const NAME_MAX = 100

export const createWalletSchema = z.object({
  name: z.string().trim().min(1, "Give the account a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  type: z.enum(WALLET_TYPES),
  subtype: z.string(),
  // Left empty, the balance is zero; it can be negative (e.g. an overdrawn account or a loan)
  initial_balance: z
    .string()
    .transform((value) => value.trim() || "0")
    .pipe(amountInput({ allowNegative: true })),
}) satisfies z.ZodType<WalletCreateInput, unknown>

export type CreateWalletFormInput = z.input<typeof createWalletSchema>
export type CreateWalletValues = z.output<typeof createWalletSchema>

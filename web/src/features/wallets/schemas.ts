import { z } from "zod"

import { amountInput } from "@/lib/amount"
import type { WalletCreateInput } from "./api"
import { WALLET_TYPES } from "./wallet-types"

const NAME_MAX = 100

export const createWalletSchema = z.object({
  name: z.string().trim().min(1, "Give the account a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  type: z.enum(WALLET_TYPES),
  // A balance can be negative (e.g. an overdrawn account)
  initial_balance: amountInput({ allowNegative: true }),
}) satisfies z.ZodType<WalletCreateInput, unknown>

export type CreateWalletFormInput = z.input<typeof createWalletSchema>
export type CreateWalletValues = z.output<typeof createWalletSchema>

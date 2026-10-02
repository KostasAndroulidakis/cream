import { z } from "zod"

import { SUPPORTED_CURRENCIES } from "@/lib/money"
import type { WalletCreateInput } from "./api"
import { WALLET_TYPES } from "./wallet-types"

// Mirrors the API (NUMERIC(19, 4)): up to 15 integer digits and 4 decimals
const AMOUNT_PATTERN = /^-?\d{1,15}(\.\d{1,4})?$/
const NAME_MAX = 100

export const createWalletSchema = z.object({
  name: z.string().trim().min(1, "Give the wallet a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  type: z.enum(WALLET_TYPES),
  currency: z.string().refine((code) => SUPPORTED_CURRENCIES.includes(code), "Pick a currency"),
  initial_balance: z
    .string()
    .trim()
    // Accept the Greek/European decimal comma: "12,50" -> "12.50"
    .transform((value) => value.replace(",", "."))
    .pipe(z.string().regex(AMOUNT_PATTERN, "Enter an amount like 250 or 1234.56")),
}) satisfies z.ZodType<WalletCreateInput, unknown>

export type CreateWalletFormInput = z.input<typeof createWalletSchema>
export type CreateWalletValues = z.output<typeof createWalletSchema>

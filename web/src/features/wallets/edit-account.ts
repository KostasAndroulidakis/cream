import { z } from "zod"

import { amountInput, isZeroAmount } from "@/lib/amount"
import type { Wallet, WalletType } from "./api"
import { WALLET_TYPES } from "./wallet-types"

const NAME_MAX = 100

export const editAccountSchema = z.object({
  name: z.string().trim().min(1, "Give the account a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  balance: amountInput({ allowNegative: true }),
  type: z.enum(WALLET_TYPES),
  subtype: z.string().min(1),
  // Optional: empty means no limit
  credit_limit: z.union([z.literal(""), amountInput({ allowNegative: false })]),
  invert_balance: z.boolean(),
  is_hidden: z.boolean(),
  exclude_balance: z.boolean(),
  hide_transactions: z.boolean(),
})

export type EditAccountInput = z.input<typeof editAccountSchema>
export type EditAccountValues = z.output<typeof editAccountSchema>

/** The one type that has a credit limit. */
export const CREDIT_CARD: WalletType = "credit_card"

/** An API amount ("11851.1000") as people type it ("11851.10"): no float, no padding past cents. */
export function editableAmount(amount: string): string {
  return amount.replace(/(\.\d{2})\d*$/, (cents) => cents.replace(/0+$/, "").padEnd(3, "0"))
}

/** The same amount with the opposite sign ("12.50" ↔ "-12.50"); zero stays zero. */
export function negate(amount: string): string {
  if (isZeroAmount(amount)) return amount
  return amount.startsWith("-") ? amount.slice(1) : `-${amount}`
}

export function formValues(wallet: Wallet): EditAccountInput {
  return {
    name: wallet.name,
    balance: editableAmount(wallet.balance),
    type: wallet.type,
    subtype: wallet.subtype,
    credit_limit: wallet.credit_limit === null ? "" : editableAmount(wallet.credit_limit),
    invert_balance: wallet.invert_balance,
    is_hidden: wallet.is_hidden,
    exclude_balance: wallet.exclude_balance,
    hide_transactions: wallet.hide_transactions,
  }
}

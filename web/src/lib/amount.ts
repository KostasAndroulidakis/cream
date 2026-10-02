import { z } from "zod"

// Mirrors the API's NUMERIC(19, 4): up to 15 integer digits and 4 decimals
const UNSIGNED_AMOUNT = /^\d{1,15}(\.\d{1,4})?$/
const SIGNED_AMOUNT = /^-?\d{1,15}(\.\d{1,4})?$/
const FORMAT_HINT = "Enter an amount like 250 or 1234.56"

/**
 * A decimal amount typed by a person. Accepts the European decimal comma ("12,50")
 * and outputs a dot-decimal string the API understands ("12.50"). Never a float.
 */
export function amountInput({ allowNegative }: { allowNegative: boolean }) {
  return z
    .string()
    .trim()
    .transform((value) => value.replace(",", "."))
    .pipe(z.string().regex(allowNegative ? SIGNED_AMOUNT : UNSIGNED_AMOUNT, FORMAT_HINT))
}

/** True when a dot-decimal string is exactly zero ("0", "0.00"). */
export function isZeroAmount(value: string): boolean {
  return /^-?0+(\.0+)?$/.test(value)
}

/** True for money coming in: the API stores income as positive and spending as negative. */
export function isMoneyIn(amount: string): boolean {
  return !amount.startsWith("-")
}

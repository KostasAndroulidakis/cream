/**
 * Exact sums of the API's decimal strings (NUMERIC(19, 4)) without floating point:
 * "12.5" becomes 125000n ten-thousandths, adds exactly, and converts back to "12.5000".
 */
const SCALE_DIGITS = 4
const SCALE = 10n ** BigInt(SCALE_DIGITS)

function toUnits(amount: string): bigint {
  const negative = amount.startsWith("-")
  const [whole, fraction = ""] = amount.replace(/^[-+]/, "").split(".")
  const units = BigInt(whole || "0") * SCALE + BigInt(fraction.padEnd(SCALE_DIGITS, "0").slice(0, SCALE_DIGITS))
  return negative ? -units : units
}

function fromUnits(units: bigint): string {
  const sign = units < 0n ? "-" : ""
  const absolute = units < 0n ? -units : units
  const fraction = String(absolute % SCALE).padStart(SCALE_DIGITS, "0")
  return `${sign}${absolute / SCALE}.${fraction}`
}

/** The exact sum of decimal strings, as a decimal string. */
export function sumAmounts(amounts: readonly string[]): string {
  return fromUnits(amounts.reduce((total, amount) => total + toUnits(amount), 0n))
}

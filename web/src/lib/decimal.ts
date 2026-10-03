import { isZeroAmount } from "./amount"

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

/** The same amount with the opposite sign ("12.50" ↔ "-12.50"); zero stays zero. */
export function negate(amount: string): string {
  if (isZeroAmount(amount)) return amount
  return amount.startsWith("-") ? amount.slice(1) : `-${amount}`
}

/** The exact difference `to - from`, as a decimal string. */
export function subtractAmounts(to: string, from: string): string {
  return sumAmounts([to, negate(from)])
}

// part / whole as a percent to one decimal ("30.7"), rounded half away from zero; whole is never zero
function percentText(part: bigint, whole: bigint): string {
  const size = whole < 0n ? -whole : whole
  const sign = part < 0n ? -1n : 1n
  const tenths = (2n * part * 1000n + sign * size) / (2n * size)
  const absolute = tenths < 0n ? -tenths : tenths
  return `${tenths < 0n ? "-" : ""}${absolute / 10n}.${absolute % 10n}`
}

/** The change from one amount to another, as a percent of the first's size, to one decimal ("30.7"). Null from zero. */
export function percentChange(from: string, to: string): string | null {
  const base = toUnits(from)
  return base === 0n ? null : percentText(toUnits(to) - base, base)
}

/** How much of a whole a part is, by size, to one decimal ("12.5"); null when the whole is zero. */
export function percentOf(part: string, whole: string): string | null {
  const total = toUnits(whole)
  if (total === 0n) return null
  const units = toUnits(part)
  return percentText(units < 0n ? -units : units, total)
}

import { isZeroAmount } from "./amount"

const formatters = new Map<string, Intl.NumberFormat>()

function formatterFor(currency: string): Intl.NumberFormat {
  let formatter = formatters.get(currency)
  if (!formatter) {
    formatter = new Intl.NumberFormat(undefined, { style: "currency", currency })
    formatters.set(currency, formatter)
  }
  return formatter
}

/**
 * Format an exact decimal string from the API (e.g. "1234.5000") as money.
 * The string is passed to Intl as-is, so no floating-point rounding happens.
 */
export function formatMoney(amount: string, currency: string): string {
  return formatterFor(currency).format(amount as Intl.StringNumericLiteral)
}

/** ISO 4217 codes the browser knows how to format. */
export const SUPPORTED_CURRENCIES: readonly string[] = Intl.supportedValuesOf("currency")

// Money in is positive, money out negative (the API's convention)
function signOf(amount: string): "positive" | "negative" | "zero" {
  if (isZeroAmount(amount)) return "zero"
  return amount.startsWith("-") ? "negative" : "positive"
}

/** Every amount with its sign: "+€10.00" money in, "-€46.30" money out, "€0.00" nothing. */
export function formatSigned(amount: string, currency: string): string {
  const unsigned = formatMoney(amount.replace(/^-/, ""), currency)
  return { positive: `+${unsigned}`, negative: `-${unsigned}`, zero: unsigned }[signOf(amount)]
}

/** The color that goes with the sign: green money in, red money out, plain for zero. */
export function amountTone(amount: string): string {
  return { positive: "text-positive", negative: "text-destructive", zero: "" }[signOf(amount)]
}

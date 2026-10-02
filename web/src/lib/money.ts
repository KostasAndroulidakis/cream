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

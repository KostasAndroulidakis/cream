import type { MerchantOrder } from "./api"

// Settings › Merchants' sort choices, as Monarch names them.
// Record<MerchantOrder, ...> makes the build fail if the API adds an order without a label.
export const MERCHANT_ORDERS: Record<MerchantOrder, string> = {
  transaction_count: "Transaction count",
  alphabetical: "Alphabetical",
}

export const DEFAULT_MERCHANT_ORDER: MerchantOrder = "transaction_count"

export function isMerchantOrder(value: string | null): value is MerchantOrder {
  return value !== null && Object.hasOwn(MERCHANT_ORDERS, value)
}

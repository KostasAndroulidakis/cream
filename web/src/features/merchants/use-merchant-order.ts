import { useSearchParamChoice } from "@/lib/use-search-param-choice"
import type { MerchantOrder } from "./api"
import { DEFAULT_MERCHANT_ORDER, isMerchantOrder } from "./order"

// The same name Monarch's Merchants URL uses (?order=TRANSACTION_COUNT)
const ORDER_PARAM = "order"

/** Settings › Merchants' sort order, kept in the URL. */
export function useMerchantOrder(): [MerchantOrder, (order: MerchantOrder) => void] {
  return useSearchParamChoice(ORDER_PARAM, isMerchantOrder, DEFAULT_MERCHANT_ORDER)
}

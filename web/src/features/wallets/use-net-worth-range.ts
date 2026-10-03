import { useSearchParamChoice } from "@/lib/use-search-param-choice"
import type { NetWorthRange } from "./api"
import { DEFAULT_NET_WORTH_RANGE, isNetWorthRange } from "./net-worth"

// The same name Monarch's Accounts URL uses (?dateRange=1M)
const RANGE_PARAM = "dateRange"

/** The net worth chart's period, kept in the URL. */
export function useNetWorthRange(): [NetWorthRange, (range: NetWorthRange) => void] {
  return useSearchParamChoice(RANGE_PARAM, isNetWorthRange, DEFAULT_NET_WORTH_RANGE)
}

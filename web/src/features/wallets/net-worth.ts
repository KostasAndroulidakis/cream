import type { NetWorthRange } from "./api"

// The chart's periods and how the dropdown and "… change" name them.
// Record<NetWorthRange, ...> makes the build fail if the API adds a range without a label.
export const NET_WORTH_RANGES: Record<NetWorthRange, string> = {
  "1M": "1 month",
  "3M": "3 months",
  "6M": "6 months",
  YTD: "Year to date",
  "1Y": "1 year",
  ALL: "All time",
}

export const DEFAULT_NET_WORTH_RANGE: NetWorthRange = "1M"

export function isNetWorthRange(value: string | null): value is NetWorthRange {
  return value !== null && Object.hasOwn(NET_WORTH_RANGES, value)
}

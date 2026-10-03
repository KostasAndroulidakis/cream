import { useSearchParamChoice } from "@/lib/use-search-param-choice"
import { DEFAULT_VIEW, isTransactionView, type TransactionView } from "./views"

// In the URL, so a link can open the page on a view (e.g. "Needs review" from the dashboard)
const VIEW_PARAM = "view"

/** The Transactions page's current view, kept in the URL. */
export function useTransactionView(): [TransactionView, (view: TransactionView) => void] {
  return useSearchParamChoice(VIEW_PARAM, isTransactionView, DEFAULT_VIEW)
}

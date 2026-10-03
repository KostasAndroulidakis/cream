import { useSearchParams } from "react-router"

import { DEFAULT_VIEW, isTransactionView, type TransactionView } from "./views"

// In the URL, so a link can open the page on a view (e.g. "Needs review" from the dashboard)
const VIEW_PARAM = "view"

/** The Transactions page's current view, kept in the URL; the default view leaves the URL clean. */
export function useTransactionView(): [TransactionView, (view: TransactionView) => void] {
  const [params, setParams] = useSearchParams()
  const value = params.get(VIEW_PARAM)
  const view = isTransactionView(value) ? value : DEFAULT_VIEW

  function setView(next: TransactionView) {
    setParams((current) => {
      const updated = new URLSearchParams(current)
      if (next === DEFAULT_VIEW) updated.delete(VIEW_PARAM)
      else updated.set(VIEW_PARAM, next)
      return updated
    })
  }

  return [view, setView]
}

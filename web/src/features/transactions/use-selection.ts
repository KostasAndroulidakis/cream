import { useCallback, useEffect, useMemo, useState } from "react"

import { isModKey } from "@/lib/keyboard"

export type Selection = {
  // "Edit multiple" mode: rows show checkboxes
  isSelecting: boolean
  selectedIds: ReadonlySet<number>
  start: () => void
  // Leave selection mode and forget the selection
  cancel: () => void
  toggle: (id: number) => void
  selectAll: (ids: readonly number[]) => void
  clear: () => void
}

/** Which transactions are picked for editing together. */
export function useSelection(): Selection {
  const [isSelecting, setIsSelecting] = useState(false)
  const [selectedIds, setSelectedIds] = useState<ReadonlySet<number>>(new Set())

  const clear = useCallback(() => setSelectedIds(new Set()), [])
  const cancel = useCallback(() => {
    setIsSelecting(false)
    setSelectedIds(new Set())
  }, [])
  const toggle = useCallback((id: number) => {
    setSelectedIds((current) => {
      const next = new Set(current)
      if (!next.delete(id)) next.add(id)
      return next
    })
  }, [])
  const selectAll = useCallback((ids: readonly number[]) => setSelectedIds(new Set(ids)), [])

  return useMemo(
    () => ({ isSelecting, selectedIds, start: () => setIsSelecting(true), cancel, toggle, selectAll, clear }),
    [isSelecting, selectedIds, cancel, toggle, selectAll, clear],
  )
}

/**
 * While selecting: Esc leaves selection mode, ⌘A / Ctrl+A selects every loaded transaction.
 * Turned off while something on top (e.g. the edit panel) owns the keyboard, so Esc closes only that.
 */
export function useSelectionShortcuts(selection: Selection, allIds: readonly number[], enabled: boolean) {
  const { isSelecting, cancel, selectAll } = selection

  useEffect(() => {
    if (!isSelecting || !enabled) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") cancel()
      else if (isModKey(event) && event.key.toLowerCase() === "a") {
        // Instead of selecting the page's text
        event.preventDefault()
        selectAll(allIds)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [isSelecting, enabled, cancel, selectAll, allIds])
}

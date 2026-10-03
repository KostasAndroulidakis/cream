import { useEffect, useRef, type ComponentProps } from "react"

import { cn } from "@/lib/utils"

type SelectionCheckboxProps = Omit<ComponentProps<"input">, "type"> & {
  // Some but not all items selected: shows a dash
  indeterminate?: boolean
}

/** A native checkbox for selecting items, with a "some selected" state. */
export function SelectionCheckbox({ indeterminate = false, className, ...props }: SelectionCheckboxProps) {
  const ref = useRef<HTMLInputElement>(null)

  // "Indeterminate" exists only as a DOM property, not as an HTML attribute
  useEffect(() => {
    if (ref.current) ref.current.indeterminate = indeterminate
  }, [indeterminate])

  return (
    <input ref={ref} type="checkbox" className={cn("size-[1.125rem] shrink-0 cursor-pointer accent-primary", className)} {...props} />
  )
}

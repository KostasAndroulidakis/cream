import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

type CheckboxFieldProps = {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  children: ReactNode
  className?: string
}

/** A native checkbox with its label; clicking the text toggles it too. */
export function CheckboxField({ checked, onCheckedChange, children, className }: CheckboxFieldProps) {
  return (
    <label className={cn("flex min-w-0 cursor-pointer items-center gap-2 text-sm text-muted-foreground", className)}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onCheckedChange(event.target.checked)}
        className="size-4 shrink-0 accent-primary"
      />
      <span className="truncate">{children}</span>
    </label>
  )
}

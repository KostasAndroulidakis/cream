import type { UseFormRegisterReturn } from "react-hook-form"

import { cn } from "@/lib/utils"
import { KIND_LABELS, TRANSACTION_KINDS, type TransactionKind } from "../kinds"

type KindToggleProps = {
  value: TransactionKind
  registration: UseFormRegisterReturn<"kind">
}

/** Expense / Income switch built from native radio inputs (keyboard and screen-reader friendly). */
export function KindToggle({ value, registration }: KindToggleProps) {
  return (
    <fieldset className="grid grid-cols-2 gap-1 rounded-lg bg-muted p-1">
      <legend className="sr-only">Type</legend>
      {TRANSACTION_KINDS.map((kind) => (
        <label
          key={kind}
          className={cn(
            "cursor-pointer rounded-md py-1.5 text-center text-sm font-medium text-muted-foreground transition-colors has-focus-visible:ring-3 has-focus-visible:ring-ring/50",
            value === kind && "bg-background text-foreground shadow-xs",
          )}
        >
          <input type="radio" value={kind} className="sr-only" {...registration} />
          {KIND_LABELS[kind]}
        </label>
      ))}
    </fieldset>
  )
}

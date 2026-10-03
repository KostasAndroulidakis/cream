import type { ReactNode } from "react"

import { Label } from "@/components/ui/label"

type FormFieldProps = {
  id: string
  // Usually text; may carry a small icon such as an info hint
  label: ReactNode
  error?: string
  children: ReactNode
}

export function FormField({ id, label, error, children }: FormFieldProps) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error && (
        <p id={`${id}-error`} className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}

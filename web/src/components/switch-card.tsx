import type { ReactNode } from "react"

import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

type SwitchCardProps = {
  id: string
  title: string
  description: ReactNode
  checked: boolean
  onCheckedChange: (checked: boolean) => void
}

/** Monarch's on/off setting: a bordered card with a title, what it does, and a switch on the right. */
export function SwitchCard({ id, title, description, checked, onCheckedChange }: SwitchCardProps) {
  return (
    <div className="flex items-center gap-4 rounded-lg border px-4 py-3.5">
      <div className="flex-1 space-y-1">
        <Label htmlFor={id} className="font-semibold">
          {title}
        </Label>
        <div className="text-sm text-muted-foreground">{description}</div>
      </div>
      <Switch id={id} checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  )
}

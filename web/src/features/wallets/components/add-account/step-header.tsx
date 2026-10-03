import { ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"
import { DialogDescription, DialogTitle } from "@/components/ui/dialog"

type StepHeaderProps = {
  title: string
  // For screen readers; Monarch's steps show no subtitle
  description: string
  // Back to the previous step; the first step has none
  onBack?: () => void
}

/** A step's title bar in the Add account dialog, with Monarch's ← above the title on later steps. */
export function StepHeader({ title, description, onBack }: StepHeaderProps) {
  return (
    <div className="space-y-3 px-6 pt-6 pb-4">
      {onBack && (
        <Button variant="ghost" size="icon-sm" className="-ml-1.5" onClick={onBack} aria-label="Back">
          <ArrowLeft className="size-5" aria-hidden />
        </Button>
      )}
      <DialogTitle className="text-xl font-semibold">{title}</DialogTitle>
      <DialogDescription className="sr-only">{description}</DialogDescription>
    </div>
  )
}

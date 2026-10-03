import type { ReactNode } from "react"
import type { LucideIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

/** What every not-yet-built control says when pointed at. */
export const COMING_SOON = "Coming soon"

type ComingSoonButtonProps = {
  icon?: LucideIcon
  children: ReactNode
}

/** A button for a feature that isn't built yet: already in its final place, visibly unavailable. */
export function ComingSoonButton({ icon: Icon, children }: ComingSoonButtonProps) {
  return (
    // aria-disabled instead of disabled: a disabled button shows no tooltip
    <Button
      variant="outline"
      aria-disabled
      title={COMING_SOON}
      className="cursor-not-allowed opacity-50 hover:bg-transparent active:not-aria-[haspopup]:translate-y-0"
    >
      {Icon && <Icon aria-hidden />}
      {children}
    </Button>
  )
}

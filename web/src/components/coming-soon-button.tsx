import type { ReactNode } from "react"
import type { LucideIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

/** What every not-yet-built control says when pointed at. */
export const COMING_SOON = "Coming soon"

// aria-disabled instead of disabled: a disabled button shows no tooltip
const UNAVAILABLE =
  "cursor-not-allowed opacity-50 hover:bg-transparent active:not-aria-[haspopup]:translate-y-0"

type ComingSoonButtonProps = {
  icon?: LucideIcon
  children: ReactNode
}

/** A button for a feature that isn't built yet: already in its final place, visibly unavailable. */
export function ComingSoonButton({ icon: Icon, children }: ComingSoonButtonProps) {
  return (
    <Button variant="outline" aria-disabled title={COMING_SOON} className={UNAVAILABLE}>
      {Icon && <Icon aria-hidden />}
      {children}
    </Button>
  )
}

/** The icon-only kind, e.g. in the sidebar header; `label` is what screen readers announce. */
export function ComingSoonIconButton({ icon: Icon, label }: { icon: LucideIcon; label: string }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-disabled
      aria-label={label}
      title={`${label}: ${COMING_SOON.toLowerCase()}`}
      className={UNAVAILABLE}
    >
      <Icon className="size-[1.125rem]" aria-hidden />
    </Button>
  )
}

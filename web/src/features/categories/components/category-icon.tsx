import { cn } from "@/lib/utils"

// Shown for a category without an emoji
const DEFAULT_ICON = "•"

/** A category's emoji (Monarch's icon), in a fixed-width slot so names line up. */
export function CategoryIcon({ icon, className }: { icon: string | null; className?: string }) {
  return (
    <span aria-hidden className={cn("w-5 shrink-0 text-center", className)}>
      {icon ?? DEFAULT_ICON}
    </span>
  )
}

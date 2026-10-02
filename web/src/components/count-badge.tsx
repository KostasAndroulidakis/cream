import { cn } from "@/lib/utils"

type CountBadgeProps = {
  count: number
  // Spoken instead of the bare number, e.g. "12 to review"
  label: string
  className?: string
}

/** A small pill with a number, e.g. next to a navigation item. */
export function CountBadge({ count, label, className }: CountBadgeProps) {
  return (
    <span
      aria-label={label}
      className={cn(
        "inline-grid min-w-5 place-items-center rounded-full bg-primary px-1.5 py-0.5 text-[0.7rem] leading-none font-semibold tabular-nums text-primary-foreground",
        className,
      )}
    >
      {count}
    </span>
  )
}

import { cn } from "@/lib/utils"

/** The user's initial in a circle, until profile photos exist. */
export function UserAvatar({ name, className }: { name: string; className?: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        "inline-grid size-12 shrink-0 place-items-center rounded-full bg-primary text-xl font-medium text-primary-foreground",
        className,
      )}
    >
      {name.charAt(0).toUpperCase()}
    </span>
  )
}

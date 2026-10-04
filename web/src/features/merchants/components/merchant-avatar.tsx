import { cn } from "@/lib/utils"

/** A round mark with the merchant's first letter, in place of a logo. */
export function MerchantAvatar({ name, className }: { name: string; className?: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        "grid size-6 shrink-0 place-items-center rounded-full bg-muted text-xs font-semibold text-muted-foreground uppercase",
        className,
      )}
    >
      {name.trim().charAt(0)}
    </span>
  )
}

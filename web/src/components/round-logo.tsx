import { useState } from "react"

import { cn } from "@/lib/utils"

type RoundLogoProps = {
  // Whose logo: its initial stands in when there's no image
  name: string
  src?: string | null
  className?: string
}

/** A round logo (a bank's, a merchant's), or the name's initial when there's none or it fails to load. */
export function RoundLogo({ name, src, className }: RoundLogoProps) {
  // The URL that failed, so a different one later gets its own try
  const [failed, setFailed] = useState<string | null>(null)

  if (src && src !== failed) {
    return (
      <img
        src={src}
        alt=""
        onError={() => setFailed(src)}
        className={cn("size-10 shrink-0 rounded-full bg-card object-contain", className)}
      />
    )
  }
  return (
    <span
      aria-hidden
      className={cn(
        "grid size-10 shrink-0 place-items-center rounded-full bg-muted font-semibold text-muted-foreground uppercase",
        className,
      )}
    >
      {name.trim().charAt(0)}
    </span>
  )
}

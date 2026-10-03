import { useState } from "react"

import { cn } from "@/lib/utils"

type BankLogoProps = {
  name: string
  logo?: string | null
  className?: string
}

/** A bank's round logo from Enable Banking, or its initial when it has none or it fails to load. */
export function BankLogo({ name, logo, className }: BankLogoProps) {
  // The URL that failed, so a different logo later gets its own try
  const [failed, setFailed] = useState<string | null>(null)

  if (logo && logo !== failed) {
    return (
      <img
        src={logo}
        alt=""
        onError={() => setFailed(logo)}
        className={cn("size-10 shrink-0 rounded-full bg-card object-contain", className)}
      />
    )
  }
  return (
    <span
      aria-hidden
      className={cn(
        "grid size-10 shrink-0 place-items-center rounded-full bg-muted font-semibold text-muted-foreground",
        className,
      )}
    >
      {name.charAt(0).toUpperCase()}
    </span>
  )
}

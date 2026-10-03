import type { ReactNode } from "react"
import { ArrowRight } from "lucide-react"

import { COMING_SOON } from "@/components/coming-soon-button"
import { cn } from "@/lib/utils"

type OptionRowProps = {
  title: string
  // The line under the title, e.g. "0 added"; unavailable options say "Coming soon"
  detail?: string
  // Logos or an icon, right-aligned before the arrow
  visual: ReactNode
  // Left out for a way to add accounts that isn't built yet
  onSelect?: () => void
}

/** One way to add accounts on the first step: "Banks & credit cards  0 added  [logos] →". */
export function OptionRow({ title, detail, visual, onSelect }: OptionRowProps) {
  const available = onSelect !== undefined
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-disabled={!available}
      title={available ? undefined : COMING_SOON}
      className={cn(
        "flex w-full items-center gap-4 rounded-xl bg-muted/60 px-5 py-4 text-left transition-colors",
        available ? "hover:bg-muted" : "cursor-not-allowed opacity-50",
      )}
    >
      <span className="min-w-0 flex-1">
        <span className="block text-base font-medium">{title}</span>
        <span className="block text-sm text-muted-foreground">{available ? detail : COMING_SOON}</span>
      </span>
      {visual}
      <ArrowRight className="size-5 shrink-0" aria-hidden />
    </button>
  )
}

/** A round white badge holding one icon, for options without logos. */
export function OptionIcon({ children }: { children: ReactNode }) {
  return (
    <span className="grid size-9 place-items-center rounded-full bg-card [&_svg]:size-[1.125rem]" aria-hidden>
      {children}
    </span>
  )
}

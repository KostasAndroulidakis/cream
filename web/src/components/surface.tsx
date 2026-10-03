import type { ReactNode } from "react"

type SurfaceProps = {
  // Names the section for screen readers
  label: string
  children: ReactNode
}

/** The white card a page's main content sits on (the transactions list, the accounts list). */
export function Surface({ label, children }: SurfaceProps) {
  return (
    <section aria-label={label} className="overflow-hidden rounded-xl border bg-card shadow-xs">
      {children}
    </section>
  )
}

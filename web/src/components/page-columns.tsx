import type { ReactNode } from "react"

/**
 * Main content and a narrower side column on large screens, stacked on phones.
 * minmax(0, …) lets long, truncated text shrink instead of widening the page.
 */
export function PageColumns({ children }: { children: ReactNode }) {
  return <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">{children}</div>
}

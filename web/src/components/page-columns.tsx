import type { ReactNode } from "react"

// "balanced": main content and a narrower side column (Dashboard);
// "summary": main content and a fixed-width summary beside it (Accounts, as in Monarch)
const LAYOUTS = {
  balanced: "lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]",
  summary: "lg:grid-cols-[minmax(0,1fr)_minmax(0,485px)]",
} as const

type PageColumnsProps = {
  layout?: keyof typeof LAYOUTS
  children: ReactNode
}

/**
 * Main content and a side column on large screens, stacked on phones.
 * minmax(0, …) lets long, truncated text shrink instead of widening the page.
 */
export function PageColumns({ layout = "balanced", children }: PageColumnsProps) {
  return <div className={`grid grid-cols-1 items-start gap-6 ${LAYOUTS[layout]}`}>{children}</div>
}

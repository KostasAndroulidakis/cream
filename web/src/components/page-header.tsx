import type { ReactNode } from "react"

type PageHeaderProps = {
  title: string
  // The page's own buttons, right-aligned (e.g. "Filters", "+ Add account")
  actions?: ReactNode
}

/**
 * The top of every page: the title on the left, the page's buttons on the right.
 * Position, typography and button height live here, so every page lines up the same way.
 */
export function PageHeader({ title, actions }: PageHeaderProps) {
  return (
    <header className="flex min-h-12 flex-wrap items-center justify-between gap-4">
      {/* Monarch's title is small, on the same line as the logo */}
      <h1 className="text-lg font-medium tracking-tight">{title}</h1>
      {actions && (
        <div className="flex flex-wrap items-center gap-2 [&_button]:h-10 [&_button]:px-3.5">
          {actions}
        </div>
      )}
    </header>
  )
}

/** The thin vertical line between groups of header buttons. */
export function PageHeaderDivider() {
  return <span aria-hidden className="mx-1 h-6 w-px bg-border" />
}

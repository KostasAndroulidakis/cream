import type { ReactNode } from "react"

type PanelProps = {
  id: string
  title: string
  action?: ReactNode
  children: ReactNode
}

/** A titled card section; the heading labels the section for screen readers. */
export function Panel({ id, title, action, children }: PanelProps) {
  return (
    <section aria-labelledby={id} className="rounded-xl border bg-card px-6 py-5 shadow-xs">
      <div className="flex min-h-8 items-center justify-between gap-4">
        <h2 id={id} className="text-lg font-semibold tracking-tight">
          {title}
        </h2>
        {action}
      </div>
      <div className="mt-2">{children}</div>
    </section>
  )
}

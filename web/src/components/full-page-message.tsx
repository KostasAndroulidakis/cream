import type { ReactNode } from "react"

type FullPageMessageProps = {
  title: string
  children?: ReactNode
}

export function FullPageMessage({ title, children }: FullPageMessageProps) {
  return (
    <main className="grid min-h-svh place-items-center p-6">
      <div className="max-w-sm space-y-3 text-center" aria-live="polite">
        <p className="text-sm font-medium">{title}</p>
        {children}
      </div>
    </main>
  )
}

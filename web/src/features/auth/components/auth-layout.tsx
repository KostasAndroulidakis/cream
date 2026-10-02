import type { ReactNode } from "react"

type AuthLayoutProps = {
  title: string
  description: string
  children: ReactNode
  footer: ReactNode
}

export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  return (
    <div className="grid min-h-svh lg:grid-cols-[5fr_6fr]">
      <aside className="flex flex-col justify-between gap-6 bg-primary px-6 py-8 text-primary-foreground sm:px-10 lg:py-12">
        <div className="space-y-3">
          <p className="text-[clamp(3rem,9vw,7.5rem)] leading-[0.85] font-semibold tracking-[-0.04em]">
            CREAM
          </p>
          <div className="h-1 w-16 bg-brass" aria-hidden />
        </div>
        <p className="hidden max-w-xs text-sm text-primary-foreground/75 lg:block">
          Every wallet, every euro, in one place. Entered by you, kept by you. No bank links.
        </p>
      </aside>

      <main className="flex items-center justify-center px-6 py-10 sm:px-10">
        <div className="w-full max-w-sm space-y-8">
          <header className="space-y-1.5">
            <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
            <p className="text-sm text-muted-foreground">{description}</p>
          </header>
          {children}
          <footer className="text-sm text-muted-foreground">{footer}</footer>
        </div>
      </main>
    </div>
  )
}

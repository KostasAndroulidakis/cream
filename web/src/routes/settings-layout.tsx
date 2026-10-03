import { NavLink, Outlet } from "react-router"

import { COMING_SOON } from "@/components/coming-soon-button"
import { PageHeader } from "@/components/page-header"
import { cn } from "@/lib/utils"
import { SETTINGS_GROUPS, type SettingsGroup, type SettingsItem } from "./settings-nav"

const ITEM = "flex h-10 items-center gap-2 rounded-lg px-5 text-[0.9375rem]"

function BetaBadge() {
  return (
    <span className="rounded-md bg-sky-100 px-1.5 py-0.5 text-[0.7rem] font-medium text-sky-700 dark:bg-sky-950 dark:text-sky-300">
      Beta
    </span>
  )
}

function SettingsLink({ item: { label, to, beta } }: { item: SettingsItem }) {
  const content = (
    <>
      {label}
      {beta && <BetaBadge />}
    </>
  )

  if (!to) {
    return (
      <span aria-disabled title={COMING_SOON} className={cn(ITEM, "cursor-not-allowed text-muted-foreground")}>
        {content}
      </span>
    )
  }

  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(ITEM, "transition-colors hover:bg-muted", isActive && "bg-primary/10 font-medium text-primary hover:bg-primary/10")
      }
    >
      {content}
    </NavLink>
  )
}

function SettingsMenuCard({ group: { title, items } }: { group: SettingsGroup }) {
  const headingId = `settings-${title.toLowerCase()}`
  return (
    <section aria-labelledby={headingId} className="rounded-xl border bg-card shadow-xs">
      <h2 id={headingId} className="border-b px-6 py-4 text-lg font-semibold tracking-tight">
        {title}
      </h2>
      <ul className="flex flex-col gap-0.5 p-1">
        {items.map((item) => (
          <li key={item.label}>
            <SettingsLink item={item} />
          </li>
        ))}
      </ul>
    </section>
  )
}

/** Settings, like Monarch's: the menu cards on the left, the chosen section on the right. */
export function SettingsLayout() {
  return (
    <div className="space-y-4">
      <PageHeader title="Settings" />
      <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] xl:grid-cols-[26rem_minmax(0,1fr)]">
        <nav aria-label="Settings" className="space-y-4">
          {SETTINGS_GROUPS.map((group) => (
            <SettingsMenuCard key={group.title} group={group} />
          ))}
        </nav>
        <Outlet />
      </div>
    </div>
  )
}

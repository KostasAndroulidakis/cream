import { NavLink } from "react-router"

import { cn } from "@/lib/utils"
import { AccountActions } from "./account-actions"
import { NAV_ITEMS } from "./nav-items"
import { Wordmark } from "./wordmark"

/** Phone and tablet navigation, in place of the sidebar: name and account on top, pages below. */
export function TopBar() {
  return (
    <header className="border-b bg-background px-4 lg:hidden">
      <div className="flex h-12 items-center justify-between">
        <Wordmark />
        <AccountActions />
      </div>
      <nav aria-label="Main" className="-mx-3 flex items-center gap-1 overflow-x-auto pb-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end, Badge }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "inline-flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground",
                isActive && "bg-sidebar-accent text-foreground",
              )
            }
          >
            <Icon className="size-4" aria-hidden />
            {label}
            {Badge && <Badge />}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}

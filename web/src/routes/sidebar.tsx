import { NavLink } from "react-router"

import { cn } from "@/lib/utils"
import { AccountActions } from "./account-actions"
import { NAV_ITEMS, type NavItem } from "./nav-items"
import { Wordmark } from "./wordmark"

function SidebarLink({ item: { to, label, icon: Icon, end, Badge } }: { item: NavItem }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex h-11 items-center gap-3 rounded-lg px-3 text-[0.9375rem] text-sidebar-foreground transition-colors hover:bg-sidebar-accent/60",
          isActive && "bg-sidebar-accent font-medium",
        )
      }
    >
      <Icon className="size-[1.125rem] shrink-0" aria-hidden />
      <span className="flex-1 truncate">{label}</span>
      {Badge && <Badge className="rounded-md" />}
    </NavLink>
  )
}

/** Desktop navigation: a full-height column on the left, on the same background as the page. */
export function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-svh w-58 shrink-0 flex-col px-2 pb-3 lg:flex">
      <div className="flex h-14 items-center px-3">
        <Wordmark />
      </div>
      <nav aria-label="Main" className="flex flex-col gap-0.5">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} />
        ))}
      </nav>
      <div className="mt-auto">
        <AccountActions />
      </div>
    </aside>
  )
}

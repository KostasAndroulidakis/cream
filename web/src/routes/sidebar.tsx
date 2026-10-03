import { useState } from "react"
import { NavLink } from "react-router"

import { cn } from "@/lib/utils"
import { AccountActions } from "./account-actions"
import { NAV_ITEMS, type NavItem } from "./nav-items"
import { SidebarToggle, SidebarTools } from "./sidebar-tools"
import { Wordmark } from "./wordmark"

// Remembered per browser; the sidebar opens expanded when storage is unavailable
const COLLAPSED_KEY = "cream.sidebar-collapsed"

function readCollapsed(): boolean {
  try {
    return localStorage.getItem(COLLAPSED_KEY) === "1"
  } catch {
    return false
  }
}

function writeCollapsed(collapsed: boolean) {
  try {
    localStorage.setItem(COLLAPSED_KEY, collapsed ? "1" : "0")
  } catch {
    // Not remembered, still works for this visit
  }
}

function SidebarLink({
  item: { to, label, icon: Icon, end, Badge },
  collapsed,
}: {
  item: NavItem
  collapsed: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      title={collapsed ? label : undefined}
      className={({ isActive }) =>
        cn(
          "flex h-10 items-center gap-3 rounded-lg px-3 text-[0.9375rem] text-sidebar-foreground transition-colors hover:bg-sidebar-accent/60",
          isActive && "bg-sidebar-accent font-medium",
        )
      }
    >
      <Icon className="size-4 shrink-0" aria-hidden />
      <span className={cn("flex-1 truncate", collapsed && "sr-only")}>{label}</span>
      {Badge && !collapsed && <Badge className="rounded-md" />}
    </NavLink>
  )
}

/** Desktop navigation: a full-height column on the left, on the same background as the page. */
export function Sidebar() {
  const [collapsed, setCollapsed] = useState(readCollapsed)

  function toggle() {
    setCollapsed(!collapsed)
    writeCollapsed(!collapsed)
  }

  return (
    <aside
      className={cn(
        "sticky top-0 hidden h-svh shrink-0 flex-col px-2 pb-3 lg:flex",
        collapsed ? "w-15" : "w-58",
      )}
    >
      {/* Collapsed, only the toggle stays: there is no room for the name and the other tools */}
      <div className={cn("flex h-16 items-center", collapsed ? "justify-center" : "justify-between pl-3")}>
        {collapsed ? (
          <SidebarToggle collapsed onToggle={toggle} />
        ) : (
          <>
            <Wordmark />
            <SidebarTools collapsed={false} onToggle={toggle} />
          </>
        )}
      </div>
      <nav aria-label="Main" className="flex flex-col">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>
      <div className="mt-auto">
        <AccountActions compact={collapsed} />
      </div>
    </aside>
  )
}

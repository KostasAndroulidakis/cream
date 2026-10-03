import { Bell, PanelLeft, Search, Settings } from "lucide-react"
import { NavLink } from "react-router"

import { ComingSoonIconButton } from "@/components/coming-soon-button"
import { Button, buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { paths } from "./paths"

type SidebarToggleProps = {
  collapsed: boolean
  onToggle: () => void
}

/** Shows or hides the sidebar's labels. */
export function SidebarToggle({ collapsed, onToggle }: SidebarToggleProps) {
  const label = collapsed ? "Expand sidebar" : "Collapse sidebar"
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onToggle}
      aria-label={label}
      aria-expanded={!collapsed}
      title={label}
    >
      <PanelLeft className="size-[1.125rem]" aria-hidden />
    </Button>
  )
}

/** Opens Settings; stays highlighted on every settings page. */
function SettingsLink() {
  return (
    <NavLink
      to={paths.settings}
      aria-label="Settings"
      title="Settings"
      className={({ isActive }) =>
        cn(buttonVariants({ variant: "ghost", size: "icon" }), isActive && "bg-sidebar-accent text-foreground")
      }
    >
      <Settings className="size-[1.125rem]" aria-hidden />
    </NavLink>
  )
}

/** Monarch's row next to the logo: search, notifications, settings, then the sidebar toggle. */
export function SidebarTools(props: SidebarToggleProps) {
  return (
    <div className="flex items-center gap-0.5">
      <ComingSoonIconButton icon={Search} label="Search" />
      <ComingSoonIconButton icon={Bell} label="Notifications" />
      <SettingsLink />
      <SidebarToggle {...props} />
    </div>
  )
}

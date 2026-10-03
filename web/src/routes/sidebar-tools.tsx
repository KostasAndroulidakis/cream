import { Bell, PanelLeft, Search, Settings } from "lucide-react"

import { ComingSoonIconButton } from "@/components/coming-soon-button"
import { Button } from "@/components/ui/button"

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

/** Monarch's row next to the logo: search, notifications, settings, then the sidebar toggle. */
export function SidebarTools(props: SidebarToggleProps) {
  return (
    <div className="flex items-center gap-0.5">
      <ComingSoonIconButton icon={Search} label="Search" />
      <ComingSoonIconButton icon={Bell} label="Notifications" />
      <ComingSoonIconButton icon={Settings} label="Settings" />
      <SidebarToggle {...props} />
    </div>
  )
}

import type { ComponentType } from "react"
import { House, Inbox, Landmark, type LucideIcon } from "lucide-react"

import { InboxCountBadge } from "@/features/categorization/components/inbox-count-badge"
import { paths } from "./paths"

export type NavItem = {
  to: string
  label: string
  icon: LucideIcon
  // Match the path exactly (the home page would otherwise match every page)
  end: boolean
  // Optional live count shown at the end of the item
  Badge?: ComponentType<{ className?: string }>
}

/** Main navigation, shared by the desktop sidebar and the phone top bar. Pages join as they are built. */
export const NAV_ITEMS: readonly NavItem[] = [
  { to: paths.home, label: "Dashboard", icon: House, end: true },
  { to: paths.review, label: "Review", icon: Inbox, end: false, Badge: InboxCountBadge },
  { to: paths.connections, label: "Banks", icon: Landmark, end: false },
]

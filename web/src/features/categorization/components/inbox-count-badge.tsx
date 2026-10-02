import { useQuery } from "@tanstack/react-query"

import { CountBadge } from "@/components/count-badge"
import { inboxQueryOptions } from "../api"

/** How many transactions wait for a category; nothing when the inbox is empty. */
export function InboxCountBadge({ className }: { className?: string }) {
  const { data } = useQuery(inboxQueryOptions)
  if (!data?.total) return null
  return <CountBadge count={data.total} label={`${data.total} to review`} className={className} />
}

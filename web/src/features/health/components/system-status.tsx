import { useQuery } from "@tanstack/react-query"

import { cn } from "@/lib/utils"
import { healthQueryOptions, type Health } from "../api"

type Status = Health["api"] | "unknown" | "checking"

const STATUS_STYLES: Record<Status, { label: string; dot: string }> = {
  ok: { label: "Operational", dot: "bg-emerald-500" },
  down: { label: "Down", dot: "bg-red-500" },
  unknown: { label: "Unknown", dot: "bg-muted-foreground/40" },
  checking: { label: "Checking…", dot: "bg-amber-400 animate-pulse" },
}

const TIME_FORMAT = new Intl.DateTimeFormat(undefined, { timeStyle: "medium" })

function StatusRow({ name, status }: { name: string; status: Status }) {
  const { label, dot } = STATUS_STYLES[status]

  return (
    <li className="flex items-center justify-between py-3">
      <span className="text-sm font-medium">{name}</span>
      <span className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className={cn("size-2 rounded-full", dot)} aria-hidden />
        {label}
      </span>
    </li>
  )
}

export function SystemStatus() {
  const { data, isPending, isError, dataUpdatedAt, errorUpdatedAt } = useQuery(healthQueryOptions)

  const apiStatus: Status = isPending ? "checking" : isError ? "down" : data.api
  const databaseStatus: Status = isPending ? "checking" : isError ? "unknown" : data.database
  const lastChecked = Math.max(dataUpdatedAt, errorUpdatedAt)

  return (
    <section className="rounded-xl border bg-card p-5 text-card-foreground shadow-sm">
      <header className="flex items-baseline justify-between">
        <h2 className="text-sm font-semibold">System status</h2>
        {lastChecked > 0 && (
          <time className="text-xs tabular-nums text-muted-foreground">
            {TIME_FORMAT.format(lastChecked)}
          </time>
        )}
      </header>
      <ul className="mt-2 divide-y">
        <StatusRow name="API" status={apiStatus} />
        <StatusRow name="Database" status={databaseStatus} />
      </ul>
    </section>
  )
}

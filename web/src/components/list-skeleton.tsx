import { cn } from "@/lib/utils"

type ListSkeletonProps = {
  rows: number
  label: string
  // Height of one row, matching the real rows so the page doesn't jump
  rowClassName: string
}

/** Placeholder rows while a list loads. */
export function ListSkeleton({ rows, label, rowClassName }: ListSkeletonProps) {
  return (
    <ul className="divide-y" aria-label={label}>
      {Array.from({ length: rows }, (_, i) => (
        <li key={i} className={cn("animate-pulse py-3", rowClassName)}>
          <div className="h-full rounded-lg bg-muted" />
        </li>
      ))}
    </ul>
  )
}

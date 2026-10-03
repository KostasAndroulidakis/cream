import { cn } from "@/lib/utils"

type SegmentedControlProps<Choice extends string> = {
  // Names the group for screen readers
  label: string
  // Each choice and how it reads, in display order
  options: Record<Choice, string>
  value: Choice
  onChange: (next: Choice) => void
}

/** A small set of mutually exclusive views side by side, e.g. "Totals | Percent". */
export function SegmentedControl<Choice extends string>({
  label,
  options,
  value,
  onChange,
}: SegmentedControlProps<Choice>) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-lg bg-muted p-0.5 text-sm">
      {(Object.entries(options) as [Choice, string][]).map(([choice, text]) => (
        <button
          key={choice}
          type="button"
          role="radio"
          aria-checked={choice === value}
          onClick={() => onChange(choice)}
          className={cn(
            "rounded-md px-3 py-1 font-medium text-muted-foreground transition-colors hover:text-foreground",
            choice === value && "bg-card text-foreground shadow-xs",
          )}
        >
          {text}
        </button>
      ))}
    </div>
  )
}

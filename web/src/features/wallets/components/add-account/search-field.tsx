import { Search, XCircle } from "lucide-react"

type SearchFieldProps = {
  value: string
  onChange: (value: string) => void
  placeholder: string
  autoFocus?: boolean
}

/** Monarch's institution search box: a magnifier, the text, and ⓧ to clear it once there's text. */
export function SearchField({ value, onChange, placeholder, autoFocus }: SearchFieldProps) {
  return (
    <div className="flex h-12 items-center gap-3 rounded-lg border px-4 focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50">
      <Search className="size-5 shrink-0 text-muted-foreground" aria-hidden />
      <input
        type="search"
        aria-label="Search institutions"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="min-w-0 flex-1 bg-transparent text-base outline-none placeholder:text-muted-foreground [&::-webkit-search-cancel-button]:hidden"
      />
      {value && (
        <button type="button" onClick={() => onChange("")} aria-label="Clear search" className="text-muted-foreground">
          <XCircle className="size-5" aria-hidden />
        </button>
      )}
    </div>
  )
}

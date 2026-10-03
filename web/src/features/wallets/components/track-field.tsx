import { COMING_SOON } from "@/components/coming-soon-button"
import { FormField } from "@/components/form-field"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Monarch's choices, in its order; tracking holdings needs the holdings feature, not built yet
const TRACK_OPTIONS = [
  { value: "holdings", label: "Holdings manually", available: false },
  { value: "balances", label: "Balances manually", available: true },
] as const

const TRACK_LABELS = Object.fromEntries(TRACK_OPTIONS.map(({ value, label }) => [value, label]))
// Balances is the only way to track for now, so it's the one shown and nothing needs saving
const CURRENT_TRACK = "balances"

/** "Track" on Add Investments Account: by holdings (coming soon) or by balance. */
export function TrackField() {
  return (
    <FormField id="wallet-track" label="Track">
      <Select items={TRACK_LABELS} value={CURRENT_TRACK}>
        <SelectTrigger id="wallet-track" className="w-full">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {TRACK_OPTIONS.map(({ value, label, available }) => (
            <SelectItem
              key={value}
              value={value}
              disabled={!available}
              title={available ? undefined : COMING_SOON}
              className={available ? undefined : "opacity-50"}
            >
              {label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </FormField>
  )
}

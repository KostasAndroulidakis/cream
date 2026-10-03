import { NativeSelect } from "@/components/native-select"
import { TRANSACTION_VIEWS, type TransactionView } from "../views"

type TransactionViewSelectProps = {
  value: TransactionView
  onChange: (view: TransactionView) => void
}

/** "All transactions" / "Needs review": which list the page shows. */
export function TransactionViewSelect({ value, onChange }: TransactionViewSelectProps) {
  return (
    <NativeSelect
      aria-label="Transactions view"
      className="h-10 min-w-48 font-medium"
      value={value}
      // The options below are exactly the views
      onChange={(event) => onChange(event.target.value as TransactionView)}
    >
      {Object.entries(TRANSACTION_VIEWS).map(([view, { label }]) => (
        <option key={view} value={view}>
          {label}
        </option>
      ))}
    </NativeSelect>
  )
}

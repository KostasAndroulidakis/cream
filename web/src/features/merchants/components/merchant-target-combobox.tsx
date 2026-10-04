import { useQuery } from "@tanstack/react-query"

import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox"
import { merchantsQueryOptions, type MerchantSummary } from "../api"

type MerchantTargetComboboxProps = {
  id: string
  // The merchant being merged away: never its own target
  excludeId: number
  value: MerchantSummary | null
  onChange: (merchant: MerchantSummary | null) => void
}

/** Monarch's "Select a merchant…": the user's other merchants, most used first, each with its count. */
export function MerchantTargetCombobox({ id, excludeId, value, onChange }: MerchantTargetComboboxProps) {
  const { data: merchants = [] } = useQuery(merchantsQueryOptions("transaction_count"))
  const targets = merchants.filter((merchant) => merchant.id !== excludeId)

  return (
    <Combobox<MerchantSummary>
      items={targets}
      value={value}
      onValueChange={onChange}
      itemToStringLabel={(merchant) => merchant.name}
      isItemEqualToValue={(merchant, current) => merchant.id === current.id}
      autoHighlight
    >
      <ComboboxInput id={id} className="h-10 w-full" placeholder="Select a merchant..." />
      <ComboboxContent>
        <ComboboxEmpty>No other merchants match.</ComboboxEmpty>
        <ComboboxList>
          {(merchant: MerchantSummary) => (
            <ComboboxItem key={merchant.id} value={merchant}>
              <span className="truncate">{merchant.name}</span>
              <span className="ml-auto text-muted-foreground tabular-nums">{merchant.transaction_count}</span>
            </ComboboxItem>
          )}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  )
}

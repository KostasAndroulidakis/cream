import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Plus } from "lucide-react"

import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox"
import { merchantsQueryOptions } from "../api"
import { choiceMatches, merchantChoices, sameMerchant, type MerchantChoice } from "../choices"

type MerchantComboboxProps = {
  id: string
  // The chosen merchant's name; empty when none is chosen
  value: string
  onChange: (name: string) => void
  className?: string
}

/** Pick one of the user's merchants by typing part of its name, or create one with a new name. */
export function MerchantCombobox({ id, value, onChange, className }: MerchantComboboxProps) {
  // By name, as a picker lists them
  const { data: merchants = [] } = useQuery(merchantsQueryOptions("alphabetical"))
  const [typed, setTyped] = useState(value)
  const selected: MerchantChoice | null = value ? { name: value, isNew: false } : null

  return (
    <Combobox<MerchantChoice>
      items={merchantChoices(merchants, typed)}
      value={selected}
      onValueChange={(choice) => onChange(choice?.name ?? "")}
      inputValue={typed}
      onInputValueChange={setTyped}
      filter={choiceMatches}
      itemToStringLabel={(choice) => choice.name}
      isItemEqualToValue={(choice, current) => sameMerchant(choice.name, current.name)}
      autoHighlight
    >
      <ComboboxInput id={id} className={className} placeholder="Search merchants..." showClear={value !== ""} />
      <ComboboxContent>
        <ComboboxEmpty>No merchants yet. Type a name to create one.</ComboboxEmpty>
        <ComboboxList>
          {(choice: MerchantChoice) => (
            <ComboboxItem key={choice.isNew ? `new:${choice.name}` : choice.name} value={choice}>
              {choice.isNew ? (
                <>
                  <Plus aria-hidden />
                  Create &ldquo;{choice.name}&rdquo;
                </>
              ) : (
                choice.name
              )}
            </ComboboxItem>
          )}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  )
}

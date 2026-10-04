import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { NativeSelect } from "@/components/native-select"
import { aspspsQueryOptions, type Aspsp } from "@/features/bank/api"
import { BANK_COUNTRIES, DEFAULT_BANK_COUNTRY, countryName } from "@/features/bank/countries"
import { RoundLogo } from "@/components/round-logo"
import { userMessage } from "@/lib/api/errors"
import { AddManualButton } from "./add-manual-button"
import { SearchField } from "./search-field"
import { searchPlaceholder } from "./search-placeholder"

const SKELETON_ROWS = 6
const ROW_HEIGHT = "h-[4.5rem]"

// Name or website contains the query, ignoring case
function matches(bank: Aspsp, query: string): boolean {
  const needle = query.trim().toLowerCase()
  return [bank.name, bank.website ?? ""].some((text) => text.toLowerCase().includes(needle))
}

/** One bank: logo, name and its website underneath, like Monarch's list. */
function BankRow({ bank, onPick }: { bank: Aspsp; onPick: (bank: Aspsp) => void }) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onPick(bank)}
        className="flex w-full items-center gap-4 rounded-xl bg-muted/60 px-5 py-3.5 text-left transition-colors hover:bg-muted"
      >
        <RoundLogo name={bank.name} src={bank.logo} />
        <span className="min-w-0">
          <span className="block truncate text-base font-medium">{bank.name}</span>
          {bank.website && <span className="block truncate text-sm text-muted-foreground">{bank.website}</span>}
        </span>
      </button>
    </li>
  )
}

type BankListStepProps = {
  // What was typed on the first step, if anything
  initialQuery: string
  onPick: (bank: Aspsp) => void
  onAddManual: () => void
}

/**
 * "Banks & credit cards": the country's most popular banks, or every bank matching the search.
 * Monarch has no country (Plaid knows yours); Enable Banking lists banks per country, so it's a choice here.
 */
export function BankListStep({ initialQuery, onPick, onAddManual }: BankListStepProps) {
  const [query, setQuery] = useState(initialQuery)
  const [country, setCountry] = useState<string>(DEFAULT_BANK_COUNTRY)
  const { data: banks, isPending, isError, error } = useQuery(aspspsQueryOptions(country))
  const popular = banks?.filter((bank) => bank.popular) ?? []
  // A country without a popular list shows all its banks
  const shown = query.trim() ? banks?.filter((bank) => matches(bank, query)) : popular.length ? popular : banks
  const heading = query.trim() ? null : popular.length ? "Most popular" : `Banks in ${countryName(country)}`

  return (
    <div className="space-y-4 px-6 pb-6">
      <SearchField value={query} onChange={setQuery} placeholder={searchPlaceholder(banks?.length)} autoFocus />

      <div className="flex items-center justify-between gap-4">
        <h3 className="text-base font-medium text-muted-foreground">{heading}</h3>
        <NativeSelect
          aria-label="Country"
          value={country}
          onChange={(event) => setCountry(event.target.value)}
          className="h-8 w-40 text-sm"
        >
          {BANK_COUNTRIES.map((code) => (
            <option key={code} value={code}>
              {countryName(code)}
            </option>
          ))}
        </NativeSelect>
      </div>

      {isError && <FormAlert message={userMessage(error)} />}
      {isPending ? (
        <ListSkeleton rows={SKELETON_ROWS} label="Loading banks" rowClassName={ROW_HEIGHT} />
      ) : (
        <ul className="max-h-[min(28rem,50svh)] space-y-2.5 overflow-y-auto">
          {shown?.map((bank) => (
            <BankRow key={bank.name} bank={bank} onPick={onPick} />
          ))}
          {shown?.length === 0 && (
            <li className="py-6 text-center text-muted-foreground">No banks match “{query.trim()}”.</li>
          )}
        </ul>
      )}

      <AddManualButton onClick={onAddManual} />
    </div>
  )
}

import { useQuery } from "@tanstack/react-query"
import { Bitcoin, Building2, ChartPie, TrendingUp, Upload } from "lucide-react"

import { aspspsQueryOptions, connectionsQueryOptions } from "@/features/bank/api"
import { RoundLogo } from "@/components/round-logo"
import { DEFAULT_BANK_COUNTRY } from "@/features/bank/countries"
import { AddManualButton } from "./add-manual-button"
import { OptionIcon, OptionRow } from "./option-row"
import { SearchField } from "./search-field"
import { searchPlaceholder } from "./search-placeholder"

// How many bank logos the first option shows, overlapping like Monarch's
const LOGO_COUNT = 3

// Three overlapping logos of banks CREAM connects to in the user's country, the most popular first
function BankLogos() {
  const { data: banks = [] } = useQuery(aspspsQueryOptions(DEFAULT_BANK_COUNTRY))
  return (
    <span className="flex -space-x-2.5" aria-hidden>
      {banks.slice(0, LOGO_COUNT).map((bank) => (
        <RoundLogo key={bank.name} name={bank.name} src={bank.logo} className="size-9 border-2 border-card" />
      ))}
    </span>
  )
}

type StartStepProps = {
  // Typing in the search continues on the bank list with that text
  onSearch: (query: string) => void
  onConnectBank: () => void
  onAddManual: () => void
}

/** "Add an account": the ways to add one, then "Add manual account" at the bottom. */
export function StartStep({ onSearch, onConnectBank, onAddManual }: StartStepProps) {
  const { data: connections = [] } = useQuery(connectionsQueryOptions)
  const { data: banks } = useQuery(aspspsQueryOptions(DEFAULT_BANK_COUNTRY))
  const linked = connections.flatMap((connection) => connection.accounts).filter((account) => account.wallet_id)

  return (
    <div className="space-y-4 px-6 pb-6">
      <SearchField value="" onChange={onSearch} placeholder={searchPlaceholder(banks?.length)} />

      <div className="space-y-2.5">
        <OptionRow
          title="Banks & credit cards"
          detail={`${linked.length} added`}
          visual={<BankLogos />}
          onSelect={onConnectBank}
        />
        <OptionRow
          title="Investments & loans"
          visual={
            <OptionIcon>
              <TrendingUp />
            </OptionIcon>
          }
        />
        <OptionRow
          title="Real estate, crypto, and more"

          visual={
            <span className="flex -space-x-2.5">
              <OptionIcon>
                <Building2 />
              </OptionIcon>
              <OptionIcon>
                <Bitcoin />
              </OptionIcon>
            </span>
          }
        />
        <OptionRow
          title="Company equity"
          visual={
            <OptionIcon>
              <ChartPie />
            </OptionIcon>
          }
        />
        <OptionRow
          title="Import transaction & balance history"
          visual={
            <OptionIcon>
              <Upload />
            </OptionIcon>
          }
        />
      </div>

      <AddManualButton onClick={onAddManual} />
    </div>
  )
}

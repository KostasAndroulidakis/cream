import { useQuery } from "@tanstack/react-query"
import { Bitcoin, Building2, ChartPie, TrendingUp, Upload, Search } from "lucide-react"

import { COMING_SOON } from "@/components/coming-soon-button"
import { Button } from "@/components/ui/button"
import { aspspsQueryOptions, connectionsQueryOptions } from "@/features/bank/api"
import { DEFAULT_BANK_COUNTRY } from "@/features/bank/countries"
import { OptionIcon, OptionRow } from "./option-row"

// How many bank logos the first option shows, overlapping like Monarch's
const LOGO_COUNT = 3

// Three overlapping logos of banks CREAM connects to in the user's country
function BankLogos() {
  const { data: banks = [] } = useQuery(aspspsQueryOptions(DEFAULT_BANK_COUNTRY))
  const logos = banks.flatMap((bank) => (bank.logo ? [bank.logo] : [])).slice(0, LOGO_COUNT)
  return (
    <span className="flex -space-x-2.5" aria-hidden>
      {logos.map((logo) => (
        <img
          key={logo}
          src={logo}
          alt=""
          className="size-9 rounded-full border-2 border-card bg-card object-contain"
        />
      ))}
    </span>
  )
}

type StartStepProps = {
  onConnectBank: () => void
  onAddManual: () => void
}

/** "Add an account": the ways to add one, then "Add manual account" at the bottom. */
export function StartStep({ onConnectBank, onAddManual }: StartStepProps) {
  const { data: connections = [] } = useQuery(connectionsQueryOptions)
  const linked = connections.flatMap((connection) => connection.accounts).filter((account) => account.wallet_id)

  return (
    <div className="space-y-4 px-6 pb-6">
      <label className="flex h-12 cursor-not-allowed items-center gap-3 rounded-lg border px-4 text-muted-foreground opacity-60">
        <Search className="size-5" aria-hidden />
        <input
          disabled
          title={COMING_SOON}
          placeholder="Search institutions…"
          className="flex-1 bg-transparent text-base outline-none"
        />
      </label>

      <div className="space-y-2.5">
        <OptionRow
          title="Banks & credit cards"
          detail={`${linked.length} added`}
          visual={<BankLogos />}
          onSelect={onConnectBank}
        />
        <OptionRow title="Investments & loans" visual={<OptionIcon><TrendingUp /></OptionIcon>} />
        <OptionRow
          title="Real estate, crypto, and more"
         
          visual={
            <span className="flex -space-x-2.5">
              <OptionIcon><Building2 /></OptionIcon>
              <OptionIcon><Bitcoin /></OptionIcon>
            </span>
          }
        />
        <OptionRow title="Company equity" visual={<OptionIcon><ChartPie /></OptionIcon>} />
        <OptionRow
          title="Import transaction & balance history"
          visual={
            <OptionIcon>
              <Upload />
            </OptionIcon>
          }
        />
      </div>

      <div className="flex justify-center pt-4">
        <Button variant="outline" size="lg" className="h-11 w-64 text-base" onClick={onAddManual}>
          Add manual account
        </Button>
      </div>
    </div>
  )
}

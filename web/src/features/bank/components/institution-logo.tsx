import { useQuery } from "@tanstack/react-query"

import { cn } from "@/lib/utils"
import { aspspsQueryOptions, type BankConnection } from "../api"
import { BankLogo } from "./bank-logo"

/** A connected bank's logo from the provider's list of banks, or its initial while that loads or has none. */
export function InstitutionLogo({ connection, className }: { connection: BankConnection; className?: string }) {
  const { data: banks } = useQuery(aspspsQueryOptions(connection.aspsp_country))
  const logo = banks?.find((bank) => bank.name === connection.aspsp_name)?.logo
  return <BankLogo name={connection.aspsp_name} logo={logo} className={cn("size-8 text-sm", className)} />
}

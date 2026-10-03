import { useQuery } from "@tanstack/react-query"

import { accountTypesQueryOptions, type WalletType } from "./api"

/** The API's catalog of account types and subtypes, with lookups for their labels. */
export function useAccountTypes() {
  const { data: catalog = [] } = useQuery(accountTypesQueryOptions)
  const byType = new Map(catalog.map((info) => [info.type, info]))

  return {
    catalog,
    typeLabel: (type: WalletType) => byType.get(type)?.label ?? "",
    subtypeLabel: (type: WalletType, subtype: string) =>
      byType.get(type)?.subtypes.find((known) => known.key === subtype)?.label ?? "",
  }
}

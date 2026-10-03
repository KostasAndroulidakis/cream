import {
  ArrowDown,
  ArrowUp,
  Award,
  Car,
  CreditCard,
  DollarSign,
  FileText,
  House,
  TrendingUp,
  type LucideIcon,
} from "lucide-react"

import type { WalletType } from "./api"

// The same symbols as Monarch's list. Labels come from the API's catalog (GET /wallets/types).
// Record<WalletType, ...> makes the build fail if the API adds a type without an icon.
export const ACCOUNT_TYPE_ICONS: Record<WalletType, LucideIcon> = {
  cash: DollarSign,
  investment: TrendingUp,
  real_estate: House,
  vehicle: Car,
  valuables: Award,
  other_asset: ArrowUp,
  credit_card: CreditCard,
  mortgage: House,
  loan: FileText,
  other_liability: ArrowDown,
}

export const WALLET_TYPES = Object.keys(ACCOUNT_TYPE_ICONS) as [WalletType, ...WalletType[]]

// What Monarch's "Add … Account" form calls a type, where it differs from the type's label
// (Mortgage opens "Add Loans Account")
const ADD_FORM_LABELS: Partial<Record<WalletType, string>> = { mortgage: "Loans" }

/** The type's name in "Add … Account" and "My … Account". */
export function addFormLabel(type: WalletType, label: string): string {
  return ADD_FORM_LABELS[type] ?? label
}

/** Types whose Add form asks how to track them (Monarch: holdings or balances, by hand). */
export const TRACKED_TYPES: ReadonlySet<WalletType> = new Set(["investment"])

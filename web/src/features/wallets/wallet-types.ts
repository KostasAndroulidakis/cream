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

/** What a new account is unless the user picks otherwise. */
export const DEFAULT_WALLET_TYPE: WalletType = "cash"

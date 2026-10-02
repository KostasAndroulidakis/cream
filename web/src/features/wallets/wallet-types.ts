import { Banknote, Landmark, Smartphone, Vault, type LucideIcon } from "lucide-react"

import type { WalletType } from "./api"

type WalletTypeMeta = { label: string; hint: string; icon: LucideIcon }

// Record<WalletType, ...> makes the build fail if the API adds a type we don't describe
export const WALLET_TYPE_META: Record<WalletType, WalletTypeMeta> = {
  bank: { label: "Bank account", hint: "Current or savings account", icon: Landmark },
  cash: { label: "Cash", hint: "What's in your pocket", icon: Banknote },
  digital: { label: "Digital wallet", hint: "PayPal, Revolut, Apple Pay", icon: Smartphone },
  stash: { label: "Stash", hint: "Money kept somewhere safe", icon: Vault },
}

export const WALLET_TYPES = Object.keys(WALLET_TYPE_META) as [WalletType, ...WalletType[]]

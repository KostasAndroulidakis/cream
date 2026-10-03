import type { Merchant } from "./api"

/** One option of the merchant picker: an existing merchant, or a new one named as typed. */
export type MerchantChoice = { name: string; isNew: boolean }

/** Spacing tidied, as the API stores names. */
export function tidyMerchantName(text: string): string {
  return text.split(/\s+/).filter(Boolean).join(" ")
}

// Same identity rule as the API: case and spacing don't make a different merchant
function merchantKey(name: string): string {
  return tidyMerchantName(name).toLocaleLowerCase()
}

export function sameMerchant(a: string, b: string): boolean {
  return merchantKey(a) === merchantKey(b)
}

/** Whether a choice stays in the list while the user types: "Create" always does. */
export function choiceMatches(choice: MerchantChoice, typed: string): boolean {
  return choice.isNew || merchantKey(choice.name).includes(merchantKey(typed))
}

/** The existing merchants, plus "Create" for a typed name that isn't one of them yet. */
export function merchantChoices(merchants: Merchant[], typed: string): MerchantChoice[] {
  const choices = merchants.map(({ name }) => ({ name, isNew: false }))
  const name = tidyMerchantName(typed)
  const isKnown = name === "" || merchants.some((merchant) => sameMerchant(merchant.name, name))
  return isKnown ? choices : [...choices, { name, isNew: true }]
}

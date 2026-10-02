/** "1 transaction", "3 transactions" (English plurals; i18n comes with the Greek UI). */
export function pluralize(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`
}

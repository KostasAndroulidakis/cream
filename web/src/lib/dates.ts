const MIDDAY_HOUR = 12

function pad(value: number): string {
  return String(value).padStart(2, "0")
}

/** Today's date in the user's time zone, as an <input type="date"> value (YYYY-MM-DD). */
export function todayInputValue(): string {
  const now = new Date()
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

/**
 * Turn a picked date into an ISO timestamp. Today keeps the current time (so the
 * newest entry sorts first); past days use local midday, safely inside that day in any zone.
 */
export function dateInputToISO(value: string): string {
  if (value === todayInputValue()) return new Date().toISOString()
  const [year, month, day] = value.split("-").map(Number)
  return new Date(year, month - 1, day, MIDDAY_HOUR).toISOString()
}

const SHORT_DATE = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short" })

export function formatShortDate(iso: string): string {
  return SHORT_DATE.format(new Date(iso))
}

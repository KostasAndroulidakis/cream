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

/** The calendar day (YYYY-MM-DD) of a timestamp in the user's time zone. */
export function localDayKey(iso: string): string {
  const date = new Date(iso)
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

const LONG_DATE = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "long", year: "numeric" })

/** A day key (YYYY-MM-DD) as a long date, e.g. "October 2, 2026". */
export function formatLongDate(dayKey: string): string {
  const [year, month, day] = dayKey.split("-").map(Number)
  return LONG_DATE.format(new Date(year, month - 1, day))
}

const RELATIVE_TIME = new Intl.RelativeTimeFormat("en", { numeric: "auto" })

// Largest unit first: the first one that fits says how long ago
const RELATIVE_UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 3600],
  ["month", 30 * 24 * 3600],
  ["week", 7 * 24 * 3600],
  ["day", 24 * 3600],
  ["hour", 3600],
  ["minute", 60],
]

/** How long ago a timestamp was, e.g. "2 hours ago", "1 month ago", "now". */
export function timeAgo(iso: string): string {
  const seconds = (Date.now() - new Date(iso).getTime()) / 1000
  for (const [unit, size] of RELATIVE_UNITS) {
    if (seconds >= size) return RELATIVE_TIME.format(-Math.floor(seconds / size), unit)
  }
  return "now"
}

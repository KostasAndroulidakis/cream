/** Every IANA timezone the browser knows, e.g. "Europe/Athens". */
export const TIMEZONES: readonly string[] = Intl.supportedValuesOf("timeZone")

/** The browser's own timezone: the choice shown until the user saves one. */
export const BROWSER_TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone

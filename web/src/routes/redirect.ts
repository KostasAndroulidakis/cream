import type { Location } from "react-router"

import { paths } from "./paths"

/** Router state carried to the login page so users land where they were headed. */
export type RedirectState = { from?: Location }

export function redirectTarget(location: Location): string {
  const from = (location.state as RedirectState | null)?.from
  return from ? `${from.pathname}${from.search}${from.hash}` : paths.home
}

import { toast } from "sonner"

// Long enough to read two lines, short enough not to linger
const NOTIFICATION_DURATION_MS = 5000
const DISMISS_LABEL = "Dismiss"

export type Notice = { title: string; description?: string }

/** A confirmation at the bottom right that closes on its own, or at once with "Dismiss". */
export function notifySuccess({ title, description }: Notice) {
  toast(title, {
    description,
    duration: NOTIFICATION_DURATION_MS,
    // Sonner closes the toast after the action runs; nothing else to do
    action: { label: DISMISS_LABEL, onClick: () => {} },
  })
}

import { toast } from "sonner"

// Long enough to read two lines, short enough not to linger
const NOTIFICATION_DURATION_MS = 5000
const DISMISS_LABEL = "Dismiss"

export type Notice = { title: string; description?: string }

// Shared by every notification: closes on its own, or at once with "Dismiss"
const NOTIFICATION_OPTIONS = {
  duration: NOTIFICATION_DURATION_MS,
  // Sonner closes the toast after the action runs; nothing else to do
  action: { label: DISMISS_LABEL, onClick: () => {} },
}

/** A confirmation at the bottom right. */
export function notifySuccess({ title, description }: Notice) {
  toast(title, { ...NOTIFICATION_OPTIONS, description })
}

/** An action that failed, for actions that have no form to show the error in. */
export function notifyError(message: string) {
  toast.error(message, NOTIFICATION_OPTIONS)
}

// Apple keyboards use ⌘ for shortcuts that other systems put on Ctrl
const IS_APPLE = /Mac|iPhone|iPad/.test(navigator.userAgent)

/** How to write the shortcut modifier in hints, e.g. "⌘A" or "Ctrl+A". */
export const MOD_KEY_PREFIX = IS_APPLE ? "⌘" : "Ctrl+"

/** True when the platform's shortcut modifier (⌘ or Ctrl) is held. */
export function isModKey(event: KeyboardEvent): boolean {
  return IS_APPLE ? event.metaKey : event.ctrlKey
}

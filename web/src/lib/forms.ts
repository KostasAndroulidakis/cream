/** Accessibility attributes linking an input to its error message. */
export function fieldA11y(id: string, error?: string) {
  return {
    "aria-invalid": error ? true : undefined,
    "aria-describedby": error ? `${id}-error` : undefined,
  }
}

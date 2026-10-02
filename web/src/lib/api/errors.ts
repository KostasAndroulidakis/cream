const FALLBACK_MESSAGE = "Something went wrong. Try again."

/** An API failure with a message that is safe to show to the user. */
export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

function extractDetail(body: unknown): string | undefined {
  if (typeof body !== "object" || body === null || !("detail" in body)) return undefined
  const { detail } = body
  if (typeof detail === "string") return detail
  // FastAPI validation errors: [{ msg: "...", ... }]
  if (Array.isArray(detail) && typeof detail[0]?.msg === "string") return detail[0].msg
  return undefined
}

/** Convert an openapi-fetch error body + response into an ApiError. */
export function toApiError(body: unknown, response: Response): ApiError {
  return new ApiError(extractDetail(body) ?? FALLBACK_MESSAGE, response.status)
}

const NETWORK_MESSAGE = "Can't reach CREAM right now. Check your connection and try again."

/** The message to show the user for any error thrown by an API call. */
export function userMessage(error: unknown): string {
  // Anything that isn't an ApiError never got a response (network down, server offline)
  return error instanceof ApiError ? error.message : NETWORK_MESSAGE
}

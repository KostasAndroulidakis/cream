import createClient from "openapi-fetch"

import type { paths } from "./schema"

// Same-origin by default: in dev, Vite proxies /api to FastAPI (see vite.config.ts)
export const api = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? "",
})

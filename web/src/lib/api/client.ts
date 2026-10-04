import createClient from "openapi-fetch"

import type { paths } from "./schema"

// Same-origin by default: in dev, Vite proxies /api to FastAPI (see vite.config.ts)
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ""

export const api = createClient<paths>({ baseUrl: API_BASE_URL })

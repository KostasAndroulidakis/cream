import { API_BASE_URL } from "@/lib/api/client"

/** Where a website's logo is served (GET /logos/{domain}: from Logo.dev, through the API). */
export function logoUrl(domain: string): string {
  return `${API_BASE_URL}/api/v1/logos/${encodeURIComponent(domain)}`
}

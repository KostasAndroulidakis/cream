import { z } from "zod"

// The API's limits (MERCHANT_MAX, WEBSITE_MAX)
const NAME_MAX = 255
const WEBSITE_MAX = 255

export const merchantSchema = z.object({
  name: z.string().trim().min(1, "Give the merchant a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  // Any form ("https://www.wolt.com/el" or "wolt.com"): the API keeps the domain, and says if it isn't one
  website: z.string().trim().max(WEBSITE_MAX, `Use at most ${WEBSITE_MAX} characters`),
})

export type MerchantValues = z.infer<typeof merchantSchema>

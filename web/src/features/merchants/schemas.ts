import { z } from "zod"

// The API's limit (MERCHANT_MAX)
const NAME_MAX = 255

export const merchantSchema = z.object({
  name: z.string().trim().min(1, "Give the merchant a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
})

export type MerchantValues = z.infer<typeof merchantSchema>

import { z } from "zod"

import type { ProfileInput } from "@/features/auth/api"
import { todayInputValue } from "@/lib/dates"

const NAME_MAX = 100
// Matches the API: a birthday before this is a typo
const EARLIEST_BIRTHDAY = "1900-01-01"

const name = (missing: string) =>
  z.string().trim().min(1, missing).max(NAME_MAX, `Use at most ${NAME_MAX} characters`)

export const profileSchema = z.object({
  first_name: name("Enter your first name"),
  last_name: name("Enter your last name"),
  // Blank falls back to the first name
  display_name: z
    .string()
    .trim()
    .max(NAME_MAX, `Use at most ${NAME_MAX} characters`)
    .transform((value) => value || null),
  // "" from an empty date input means no birthday
  birthday: z
    .string()
    .refine((value) => !value || (value >= EARLIEST_BIRTHDAY && value <= todayInputValue()), "Pick a past date")
    .transform((value) => value || null),
  timezone: z.string().min(1),
}) satisfies z.ZodType<ProfileInput, unknown>

export type ProfileFormInput = z.input<typeof profileSchema>
export type ProfileValues = z.output<typeof profileSchema>

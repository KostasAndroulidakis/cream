import { z } from "zod"

import type { LoginInput, SignupInput } from "./api"

// Mirrors the API's validation rules (api/app/schemas/user.py). The API stays the authority;
// these exist so users get instant feedback. `satisfies` breaks the build if the shapes drift.
const USERNAME_MIN = 3
const USERNAME_MAX = 50
const PASSWORD_MIN = 8
const NAME_MAX = 100

export const loginSchema = z.object({
  username: z.string().trim().min(1, "Enter your username"),
  password: z.string().min(1, "Enter your password"),
}) satisfies z.ZodType<LoginInput>

export const signupSchema = z.object({
  first_name: z.string().trim().min(1, "Enter your first name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  last_name: z.string().trim().min(1, "Enter your last name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`),
  username: z
    .string()
    .trim()
    .min(USERNAME_MIN, `Use at least ${USERNAME_MIN} characters`)
    .max(USERNAME_MAX, `Use at most ${USERNAME_MAX} characters`),
  email: z.email("Enter a valid email address"),
  password: z.string().min(PASSWORD_MIN, `Use at least ${PASSWORD_MIN} characters`),
}) satisfies z.ZodType<SignupInput>

export type LoginValues = z.infer<typeof loginSchema>
export type SignupValues = z.infer<typeof signupSchema>

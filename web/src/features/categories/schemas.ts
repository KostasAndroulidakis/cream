import { z } from "zod"

const NAME_MAX = 100

const name = z.string().trim().min(1, "Enter a name").max(NAME_MAX, `Use at most ${NAME_MAX} characters`)

export const groupSchema = z.object({
  name,
  budget_by: z.enum(["category", "group"]),
})

export type GroupValues = z.infer<typeof groupSchema>

export const categorySchema = z.object({
  icon: z.string().nullable(),
  name,
  group_id: z.number({ error: "Pick a group" }),
  exclude_from_budget: z.boolean(),
})

export type CategoryValues = z.infer<typeof categorySchema>

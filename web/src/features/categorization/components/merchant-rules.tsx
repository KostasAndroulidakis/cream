import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Trash2 } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { Button } from "@/components/ui/button"
import { categoriesQueryOptions } from "@/features/categories/api"
import { categoriesById } from "@/features/categories/grouping"
import { userMessage } from "@/lib/api/errors"
import { rulesQueryOptions, useDeleteRule } from "../api"

const SKELETON_ROWS = 3

/** The user's "always put this merchant in this category" rules, with a way to forget one. */
export function MerchantRules() {
  const rules = useQuery(rulesQueryOptions)
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const deleteRule = useDeleteRule()

  if (rules.isPending) return <ListSkeleton rows={SKELETON_ROWS} label="Loading rules" rowClassName="h-14" />
  if (rules.isError) return <FormAlert message={userMessage(rules.error)} />

  if (rules.data.length === 0) {
    return (
      <p className="py-6 text-sm text-muted-foreground">
        No rules yet. Keep <span className="font-medium text-foreground">Always use for…</span> ticked while you
        review, and CREAM remembers the merchant for every future import.
      </p>
    )
  }

  const categoryById = categoriesById(categories)

  return (
    <div className="space-y-2">
      {deleteRule.isError && <FormAlert message={userMessage(deleteRule.error)} />}
      <ul className="divide-y">
        {rules.data.map((rule) => (
          <li key={rule.id} className="flex items-center gap-3 py-3">
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{rule.merchant_name}</p>
              <p className="flex items-center gap-1.5 truncate text-sm text-muted-foreground">
                <ArrowRight className="size-3.5 shrink-0" aria-label="goes to" />
                {categoryById.get(rule.category_id)?.name}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={`Forget the rule for ${rule.merchant_name}`}
              title="Forget rule (transactions keep their categories)"
              disabled={deleteRule.isPending}
              onClick={() => deleteRule.mutate(rule.id)}
            >
              <Trash2 aria-hidden />
            </Button>
          </li>
        ))}
      </ul>
    </div>
  )
}

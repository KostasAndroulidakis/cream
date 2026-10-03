import { useState, type FormEvent } from "react"
import { useQuery } from "@tanstack/react-query"

import { CheckboxField } from "@/components/checkbox-field"
import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { categoriesQueryOptions } from "@/features/categories/api"
import { CategorySelect } from "@/features/categories/components/category-select"
import { categoriesById, groupAssignableCategories, NO_CATEGORY } from "@/features/categories/grouping"
import type { Transaction } from "@/features/transactions/api"
import { transactionLabel } from "@/features/transactions/display"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { useCategorizeTransaction } from "../api"
import { categoryTypesFor } from "../category-choices"
import { describeResult } from "../result-message"

type CategorizeFormProps = {
  transaction: Transaction
  // Inline fits a list row; stacked fits a dialog
  layout: "inline" | "stacked"
  // Receives a one-sentence summary of what changed
  onCategorized: (message: string) => void
}

/** Pick a category for one transaction, optionally remembering it for the merchant. */
export function CategorizeForm({ transaction, layout, onCategorized }: CategorizeFormProps) {
  const categorize = useCategorizeTransaction()
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const [categoryId, setCategoryId] = useState(NO_CATEGORY)
  // A rule needs a merchant to match on. Ticked by default only for a named counterparty:
  // bank texts often carry one-off details (card numbers, dates) that never repeat.
  const canRemember = transaction.merchant_key !== null
  const [applyToSimilar, setApplyToSimilar] = useState(canRemember && transaction.counterparty !== null)
  const merchant = transactionLabel(transaction)
  const isInline = layout === "inline"

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (categoryId === NO_CATEGORY) return
    categorize.mutate(
      { transactionId: transaction.id, categoryId: Number(categoryId), applyToSimilar: canRemember && applyToSimilar },
      {
        onSuccess: (result) =>
          onCategorized(describeResult(result, categoriesById(categories).get(result.transaction.category_id)?.name ?? "")),
      },
    )
  }

  return (
    <form
      onSubmit={onSubmit}
      className={cn(isInline ? "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-3 gap-y-2.5 sm:pl-16" : "space-y-4")}
    >
      <div>
        <CategorySelect
          aria-label={`Category for ${merchant ?? "this transaction"}`}
          value={categoryId}
          onChange={(event) => setCategoryId(event.target.value)}
          groups={groupAssignableCategories(categories, categoryTypesFor(transaction.amount))}
          className={cn(!isInline && "h-9")}
        />
      </div>

      {canRemember && (
        <CheckboxField
          checked={applyToSimilar}
          onCheckedChange={setApplyToSimilar}
          className={cn(isInline && "col-span-2 row-start-2")}
        >
          Always use for <span className="font-medium text-foreground">{merchant}</span>
        </CheckboxField>
      )}

      <Button
        type="submit"
        size={isInline ? "default" : "lg"}
        // Inline, the button sits next to the picker; the checkbox goes below both
        className={cn(isInline ? "col-start-2 row-start-1 px-4" : "w-full")}
        disabled={categoryId === NO_CATEGORY || categorize.isPending}
      >
        {categorize.isPending ? "Saving…" : "Save"}
      </Button>

      {categorize.isError && (
        <div className={cn(isInline && "col-span-2")}>
          <FormAlert message={userMessage(categorize.error)} />
        </div>
      )}
    </form>
  )
}

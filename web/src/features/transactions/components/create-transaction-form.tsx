import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { useForm, useWatch } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { categoriesQueryOptions } from "@/features/categories/api"
import { CategorySelect } from "@/features/categories/components/category-select"
import { groupAssignableCategories, NO_CATEGORY } from "@/features/categories/grouping"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { dateInputToISO, todayInputValue } from "@/lib/dates"
import { fieldA11y } from "@/lib/forms"
import { useCreateTransaction } from "../api"
import { KIND_LABELS, signedAmount } from "../kinds"
import { createTransactionSchema, type CreateTransactionFormInput, type CreateTransactionValues } from "../schemas"
import { KindToggle } from "./kind-toggle"

const NO_WALLET = ""

export function CreateTransactionForm({ onCreated }: { onCreated: () => void }) {
  const createTransaction = useCreateTransaction()
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)

  const {
    register,
    handleSubmit,
    control,
    resetField,
    formState: { errors },
  } = useForm<CreateTransactionFormInput, unknown, CreateTransactionValues>({
    resolver: zodResolver(createTransactionSchema),
    defaultValues: {
      kind: "expense",
      amount: "",
      category_id: NO_CATEGORY,
      wallet_id: wallets.length === 1 ? String(wallets[0].id) : NO_WALLET,
      date: todayInputValue(),
      description: "",
    },
  })
  const kind = useWatch({ control, name: "kind" })
  const categoryGroups = groupAssignableCategories(categories, [kind])

  const onSubmit = handleSubmit(({ kind, amount, category_id, wallet_id, date, description }) =>
    createTransaction.mutate(
      {
        wallet_id,
        category_id,
        amount: signedAmount(amount, kind),
        occurred_at: dateInputToISO(date),
        description: description || null,
      },
      { onSuccess: onCreated },
    ),
  )

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      {createTransaction.isError && <FormAlert message={userMessage(createTransaction.error)} />}

      <KindToggle
        value={kind}
        registration={register("kind", {
          // A category of the other kind would be invalid, so clear the choice
          onChange: () => resetField("category_id", { defaultValue: NO_CATEGORY }),
        })}
      />

      <FormField id="tx-amount" label="Amount" error={errors.amount?.message}>
        <Input
          id="tx-amount"
          inputMode="decimal"
          placeholder="0,00"
          autoFocus
          className="h-11 text-xl font-semibold tabular-nums md:text-xl"
          {...fieldA11y("tx-amount", errors.amount?.message)}
          {...register("amount")}
        />
      </FormField>

      <FormField id="tx-category" label="Category" error={errors.category_id?.message}>
        <CategorySelect
          id="tx-category"
          groups={categoryGroups}
          {...fieldA11y("tx-category", errors.category_id?.message)}
          {...register("category_id")}
        />
      </FormField>

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField id="tx-wallet" label="Wallet" error={errors.wallet_id?.message}>
          <NativeSelect id="tx-wallet" {...fieldA11y("tx-wallet", errors.wallet_id?.message)} {...register("wallet_id")}>
            <option value={NO_WALLET} disabled>
              Pick a wallet
            </option>
            {wallets.map((wallet) => (
              <option key={wallet.id} value={wallet.id}>
                {wallet.name} ({wallet.currency})
              </option>
            ))}
          </NativeSelect>
        </FormField>

        <FormField id="tx-date" label="Date" error={errors.date?.message}>
          <Input
            id="tx-date"
            type="date"
            max={todayInputValue()}
            {...fieldA11y("tx-date", errors.date?.message)}
            {...register("date")}
          />
        </FormField>
      </div>

      <FormField id="tx-description" label="Note (optional)" error={errors.description?.message}>
        <Input
          id="tx-description"
          placeholder="e.g. Weekly groceries"
          {...fieldA11y("tx-description", errors.description?.message)}
          {...register("description")}
        />
      </FormField>

      <Button type="submit" size="lg" className="w-full" disabled={createTransaction.isPending}>
        {createTransaction.isPending ? "Saving…" : `Add ${KIND_LABELS[kind].toLowerCase()}`}
      </Button>
    </form>
  )
}

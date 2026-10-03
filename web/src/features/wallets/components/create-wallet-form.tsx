import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { SUPPORTED_CURRENCIES } from "@/lib/money"
import { useCreateWallet } from "../api"
import { createWalletSchema, type CreateWalletFormInput, type CreateWalletValues } from "../schemas"
import { WALLET_TYPE_META, WALLET_TYPES } from "../wallet-types"

const DEFAULT_VALUES: CreateWalletFormInput = {
  name: "",
  type: "bank",
  currency: "EUR",
  initial_balance: "0",
}

export function CreateWalletForm({ onCreated }: { onCreated: () => void }) {
  const createWallet = useCreateWallet()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateWalletFormInput, unknown, CreateWalletValues>({
    resolver: zodResolver(createWalletSchema),
    defaultValues: DEFAULT_VALUES,
  })

  const onSubmit = handleSubmit((values) => createWallet.mutate(values, { onSuccess: onCreated }))

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      {createWallet.isError && <FormAlert message={userMessage(createWallet.error)} />}

      <FormField id="wallet-name" label="Name" error={errors.name?.message}>
        <Input
          id="wallet-name"
          placeholder="e.g. Piraeus Bank"
          autoFocus
          {...fieldA11y("wallet-name", errors.name?.message)}
          {...register("name")}
        />
      </FormField>

      <FormField id="wallet-type" label="Type" error={errors.type?.message}>
        <NativeSelect id="wallet-type" {...register("type")}>
          {WALLET_TYPES.map((type) => (
            <option key={type} value={type}>
              {WALLET_TYPE_META[type].label} ({WALLET_TYPE_META[type].hint})
            </option>
          ))}
        </NativeSelect>
      </FormField>

      <div className="grid gap-4 sm:grid-cols-[7rem_1fr]">
        <FormField id="wallet-currency" label="Currency" error={errors.currency?.message}>
          <NativeSelect id="wallet-currency" {...fieldA11y("wallet-currency", errors.currency?.message)} {...register("currency")}>
            {SUPPORTED_CURRENCIES.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </NativeSelect>
        </FormField>

        <FormField id="wallet-balance" label="Current balance" error={errors.initial_balance?.message}>
          <Input
            id="wallet-balance"
            inputMode="decimal"
            className="tabular-nums"
            {...fieldA11y("wallet-balance", errors.initial_balance?.message)}
            {...register("initial_balance")}
          />
        </FormField>
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={createWallet.isPending}>
        {createWallet.isPending ? "Adding account…" : "Add account"}
      </Button>
    </form>
  )
}

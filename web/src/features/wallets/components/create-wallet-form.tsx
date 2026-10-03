import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { useCreateWallet } from "../api"
import { createWalletSchema, type CreateWalletFormInput, type CreateWalletValues } from "../schemas"
import { useAccountTypes } from "../use-account-types"
import { DEFAULT_WALLET_TYPE } from "../wallet-types"

const DEFAULT_VALUES: CreateWalletFormInput = {
  name: "",
  type: DEFAULT_WALLET_TYPE,
  initial_balance: "0",
}

export function CreateWalletForm({ onCreated }: { onCreated: () => void }) {
  const createWallet = useCreateWallet()
  const { catalog } = useAccountTypes()
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
          {catalog.map(({ type, label }) => (
            <option key={type} value={type}>
              {label}
            </option>
          ))}
        </NativeSelect>
      </FormField>

      {/* EUR only for now: the API gives every new account its one currency */}
      <FormField id="wallet-balance" label="Current balance" error={errors.initial_balance?.message}>
        <Input
          id="wallet-balance"
          inputMode="decimal"
          className="tabular-nums"
          {...fieldA11y("wallet-balance", errors.initial_balance?.message)}
          {...register("initial_balance")}
        />
      </FormField>

      <Button type="submit" size="lg" className="w-full" disabled={createWallet.isPending}>
        {createWallet.isPending ? "Adding account…" : "Add account"}
      </Button>
    </form>
  )
}

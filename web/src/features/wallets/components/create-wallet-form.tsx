import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { useCreateWallet, type WalletType } from "../api"
import { createWalletSchema, type CreateWalletFormInput, type CreateWalletValues } from "../schemas"
type CreateWalletFormProps = {
  // Chosen on the step before (Add Manual Account)
  type: WalletType
  onCreated: () => void
}

export function CreateWalletForm({ type, onCreated }: CreateWalletFormProps) {
  const createWallet = useCreateWallet()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateWalletFormInput, unknown, CreateWalletValues>({
    resolver: zodResolver(createWalletSchema),
    defaultValues: { name: "", type, initial_balance: "0" },
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

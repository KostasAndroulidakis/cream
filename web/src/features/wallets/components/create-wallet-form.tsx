import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm, useWatch } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormDialogBody, FormDialogFooter } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { APP_CURRENCY, formatMoney } from "@/lib/money"
import { useCreateWallet, type AccountTypeInfo } from "../api"
import { createWalletSchema, type CreateWalletFormInput, type CreateWalletValues } from "../schemas"
import { TRACKED_TYPES, addFormLabel } from "../wallet-types"
import { TrackField } from "./track-field"

type CreateWalletFormProps = {
  // Chosen on the step before (Add Manual Account)
  typeInfo: AccountTypeInfo
  onCreated: () => void
  onCancel: () => void
}

/**
 * Monarch's "Add … Account" form: Name, Type (the subtypes offered by hand, when there's a choice),
 * Track (investments), Balance; Cancel and Save.
 */
export function CreateWalletForm({ typeInfo, onCreated, onCancel }: CreateWalletFormProps) {
  const createWallet = useCreateWallet()
  const subtypes = typeInfo.subtypes.filter((subtype) => subtype.manual)
  const subtypeLabels = Object.fromEntries(subtypes.map((subtype) => [subtype.key, subtype.label]))
  const label = addFormLabel(typeInfo.type, typeInfo.label)
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateWalletFormInput, unknown, CreateWalletValues>({
    resolver: zodResolver(createWalletSchema),
    // Monarch preselects the first subtype and leaves Name and Balance empty
    defaultValues: {
      name: "",
      type: typeInfo.type,
      subtype: subtypes[0]?.key ?? "",
      initial_balance: "",
    },
  })
  const name = useWatch({ control, name: "name" })

  const onSubmit = handleSubmit((values) => createWallet.mutate(values, { onSuccess: onCreated }))

  return (
    <form onSubmit={onSubmit} noValidate>
      <FormDialogBody className="pt-0">
        {createWallet.isError && <FormAlert message={userMessage(createWallet.error)} />}

        <FormField id="wallet-name" label="Name" error={errors.name?.message}>
          <Input
            id="wallet-name"
            placeholder={`My ${label} Account`}
            autoFocus
            {...fieldA11y("wallet-name", errors.name?.message)}
            {...register("name")}
          />
        </FormField>

        {/* One subtype (e.g. Mortgage) leaves nothing to choose, so Monarch shows no Type */}
        {subtypes.length > 1 && (
          <FormField id="wallet-subtype" label="Type">
            <Controller
              control={control}
              name="subtype"
              render={({ field }) => (
                <Select
                  items={subtypeLabels}
                  value={field.value}
                  onValueChange={(next) => next !== null && field.onChange(next)}
                >
                  <SelectTrigger id="wallet-subtype" className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  {/* No height cap: Monarch shows every subtype at once (Loans has 12) */}
                  <SelectContent>
                    {subtypes.map((subtype) => (
                      <SelectItem key={subtype.key} value={subtype.key}>
                        {subtype.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </FormField>
        )}

        {TRACKED_TYPES.has(typeInfo.type) && <TrackField />}

        {/* EUR only for now: the API gives every new account its one currency */}
        <FormField id="wallet-balance" label="Balance" error={errors.initial_balance?.message}>
          <Input
            id="wallet-balance"
            inputMode="decimal"
            placeholder={formatMoney("0", APP_CURRENCY)}
            className="tabular-nums"
            {...fieldA11y("wallet-balance", errors.initial_balance?.message)}
            {...register("initial_balance")}
          />
        </FormField>
      </FormDialogBody>

      <FormDialogFooter>
        <Button type="button" variant="outline" className="ml-auto" onClick={onCancel}>
          Cancel
        </Button>
        {/* Like Monarch's, Save waits for a name */}
        <Button type="submit" disabled={!name.trim() || createWallet.isPending}>
          {createWallet.isPending ? "Saving…" : "Save"}
        </Button>
      </FormDialogFooter>
    </form>
  )
}

import { useState, type ReactNode } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm, useWatch } from "react-hook-form"

import { COMING_SOON } from "@/components/coming-soon-button"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { FormAlert } from "@/components/form-alert"
import { FormDialog } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { SwitchCard } from "@/components/switch-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { negate } from "@/lib/decimal"
import { formatMoney } from "@/lib/money"
import { notifySuccess } from "@/lib/notify"
import { useDeleteWallet, useUpdateWallet, type Wallet } from "../api"
import {
  CREDIT_CARD,
  editAccountSchema,
  formValues,
  type EditAccountInput,
  type EditAccountValues,
} from "../edit-account"
import { useAccountTypes } from "../use-account-types"

function SectionTitle({ children }: { children: string }) {
  return <h3 className="pt-2 text-base font-semibold">{children}</h3>
}

/** One of the Actions rows: what it does on the left, its button on the right. */
function ActionCard({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <div className="flex items-center gap-4 rounded-lg border px-4 py-3.5">
      <div className="flex-1 space-y-1">
        <p className="text-[0.9375rem] font-semibold">{title}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {children}
    </div>
  )
}

function EditAccountForm({ wallet, logo, onDone }: { wallet: Wallet; logo: ReactNode; onDone: () => void }) {
  const update = useUpdateWallet()
  const remove = useDeleteWallet()
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const { catalog } = useAccountTypes()
  const {
    register,
    control,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<EditAccountInput, unknown, EditAccountValues>({
    resolver: zodResolver(editAccountSchema),
    defaultValues: formValues(wallet),
  })
  const [type, balance, invert] = useWatch({ control, name: ["type", "balance", "invert_balance"] })

  const typeInfo = catalog.find((info) => info.type === type)
  const typeLabels = Object.fromEntries(catalog.map((info) => [info.type, info.label]))
  const subtypeLabels = Object.fromEntries((typeInfo?.subtypes ?? []).map((subtype) => [subtype.key, subtype.label]))
  // What Save will leave: turning "Invert" on or off flips the sign of the balance above
  const flips = invert !== wallet.invert_balance
  const preview = /^-?\d+([.,]\d+)?$/.test(balance.trim())
    ? formatMoney(flips ? negate(balance.trim().replace(",", ".")) : balance.trim().replace(",", "."), wallet.currency)
    : "—"

  const onSubmit = handleSubmit(({ credit_limit, ...values }) =>
    update.mutate(
      {
        id: wallet.id,
        changes: {
          ...values,
          // Only credit cards have a limit; other types drop it
          credit_limit: values.type === CREDIT_CARD && credit_limit !== "" ? credit_limit : null,
        },
      },
      {
        onSuccess: () => {
          onDone()
          notifySuccess({ title: "Account updated" })
        },
      },
    ),
  )

  return (
    <>
      <FormDialog
        open
        onOpenChange={(open) => !open && onDone()}
        title="Edit Account"
        description="The account's name, balance, type, and how it shows in CREAM."
        onSubmit={onSubmit}
        footer={
          <>
            <Button type="button" variant="outline" className="ml-auto px-4" onClick={onDone}>
              Cancel
            </Button>
            <Button type="submit" className="px-4" disabled={update.isPending}>
              {update.isPending ? "Saving…" : "Save"}
            </Button>
          </>
        }
      >
        {update.isError && <FormAlert message={userMessage(update.error)} />}

        <div className="flex items-center gap-4">
          {logo}
          <Button
            type="button"
            variant="outline"
            aria-disabled
            title={`Account photo: ${COMING_SOON.toLowerCase()}`}
            className="cursor-not-allowed"
          >
            Choose photo
          </Button>
        </div>

        <FormField id="account-name" label="Name" error={errors.name?.message}>
          <Input id="account-name" className="h-10" {...fieldA11y("account-name", errors.name?.message)} {...register("name")} />
        </FormField>

        <FormField id="account-balance" label="Balance" error={errors.balance?.message}>
          <Input
            id="account-balance"
            inputMode="decimal"
            className="h-10 tabular-nums"
            {...fieldA11y("account-balance", errors.balance?.message)}
            {...register("balance")}
          />
        </FormField>

        <FormField id="account-type" label="Type">
          <Controller
            control={control}
            name="type"
            render={({ field }) => (
              <Select
                items={typeLabels}
                value={field.value}
                onValueChange={(next) => {
                  if (next === null || next === field.value) return
                  field.onChange(next)
                  // A new type starts at its first subtype, as when creating an account
                  const first = catalog.find((info) => info.type === next)?.subtypes[0]?.key
                  if (first) setValue("subtype", first)
                }}
              >
                <SelectTrigger id="account-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="max-h-80">
                  {catalog.map((info) => (
                    <SelectItem key={info.type} value={info.type}>
                      {info.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </FormField>

        <FormField id="account-subtype" label="Subtype">
          <Controller
            control={control}
            name="subtype"
            render={({ field }) => (
              <Select items={subtypeLabels} value={field.value} onValueChange={(next) => next !== null && field.onChange(next)}>
                <SelectTrigger id="account-subtype">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="max-h-80">
                  {(typeInfo?.subtypes ?? []).map((subtype) => (
                    <SelectItem key={subtype.key} value={subtype.key}>
                      {subtype.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </FormField>

        {type === CREDIT_CARD && (
          <FormField id="account-credit-limit" label="Credit limit" error={errors.credit_limit?.message}>
            <Input
              id="account-credit-limit"
              inputMode="decimal"
              placeholder="Enter credit limit"
              className="h-10 tabular-nums"
              {...fieldA11y("account-credit-limit", errors.credit_limit?.message)}
              {...register("credit_limit")}
            />
          </FormField>
        )}

        <SectionTitle>Balance</SectionTitle>
        <Controller
          control={control}
          name="invert_balance"
          render={({ field }) => (
            <SwitchCard
              id="account-invert"
              title="Invert account balance"
              description={
                <>
                  <p>This will invert your account balance if updates from your bank are not syncing correctly.</p>
                  <p className="mt-3 text-foreground">Balance preview: {preview}</p>
                </>
              }
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          )}
        />

        <SectionTitle>Visibility</SectionTitle>
        <div className="space-y-3">
          {(
            [
              ["is_hidden", "Hide account", "This will hide the account from your Accounts page"],
              [
                "exclude_balance",
                "Exclude account balance",
                "This will exclude this account's balance from your total balance and account group totals",
              ],
              [
                "hide_transactions",
                "Hide transactions",
                "This will hide this account's transactions from all transactions lists and statistics.",
              ],
            ] as const
          ).map(([name, title, description]) => (
            <Controller
              key={name}
              control={control}
              name={name}
              render={({ field }) => (
                <SwitchCard
                  id={`account-${name}`}
                  title={title}
                  description={description}
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              )}
            />
          ))}
        </div>

        <SectionTitle>Actions</SectionTitle>
        <div className="space-y-3">
          <ActionCard title="Close account" description="Set balance to €0 but keep historical information">
            <Button type="button" variant="outline" aria-disabled title={COMING_SOON} className="cursor-not-allowed">
              Close
            </Button>
          </ActionCard>
          <ActionCard title="Delete account" description="Remove all data about this account from CREAM">
            <Button
              type="button"
              variant="outline"
              className="text-destructive hover:text-destructive"
              onClick={() => {
                remove.reset()
                setConfirmingDelete(true)
              }}
            >
              Delete
            </Button>
          </ActionCard>
        </div>
      </FormDialog>

      <ConfirmDialog
        open={confirmingDelete}
        onOpenChange={setConfirmingDelete}
        title={`Delete ${wallet.name}?`}
        description="The account and all its transactions are deleted for good. Its bank stays connected; the bank account just isn't linked to anything until you link it again."
        confirmLabel="Delete"
        confirmVariant="destructive"
        isPending={remove.isPending}
        errorMessage={remove.isError ? userMessage(remove.error) : undefined}
        onConfirm={() =>
          remove.mutate(wallet.id, {
            onSuccess: () => {
              setConfirmingDelete(false)
              onDone()
              notifySuccess({ title: `${wallet.name} deleted` })
            },
          })
        }
      />
    </>
  )
}

/** Monarch's Edit Account dialog, opened from an account's "Edit" button. */
export function EditAccountDialog({
  wallet,
  logo,
  trigger,
}: {
  wallet: Wallet
  // The account's picture at the top: its bank's logo, or an initial
  logo: ReactNode
  trigger: (open: () => void) => ReactNode
}) {
  const [open, setOpen] = useState(false)
  return (
    <>
      {trigger(() => setOpen(true))}
      {/* Mounted only while open: every opening starts from the account as it is now */}
      {open && <EditAccountForm wallet={wallet} logo={logo} onDone={() => setOpen(false)} />}
    </>
  )
}

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { Pencil } from "lucide-react"

import { COMING_SOON, ComingSoonButton } from "@/components/coming-soon-button"
import { FormAlert } from "@/components/form-alert"
import { FormDialog } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { SwitchCard } from "@/components/switch-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { notifySuccess } from "@/lib/notify"
import { useUpdateMerchant, type MerchantSummary } from "../api"
import { merchantSchema, type MerchantValues } from "../schemas"
import { MerchantLogo } from "./merchant-logo"
import { MergeAndDeleteButton } from "./merge-and-delete-button"

// Monarch's words; the Recurring section isn't built yet
const RECURRING_HINT = `This merchant will show on the Recurring section with expected upcoming transactions. ${COMING_SOON}.`

// CREAM's addition to Monarch's dialog: Plaid gives Monarch the logos; CREAM finds them by website
const WEBSITE_HINT = "The logo comes from here. Leave it empty for CREAM's own, if it knows the merchant."

type EditMerchantFormProps = {
  merchant: MerchantSummary
  onDone: () => void
}

/** Monarch's Edit merchant: photo, name and the recurring switch; Merge & delete, Cancel and Save below. */
function EditMerchantForm({ merchant, onDone }: EditMerchantFormProps) {
  const update = useUpdateMerchant()
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<MerchantValues>({
    resolver: zodResolver(merchantSchema),
    defaultValues: { name: merchant.name, website: merchant.website ?? "" },
  })

  const onSubmit = handleSubmit(({ name, website }) =>
    update.mutate(
      { id: merchant.id, name, website },
      {
        onSuccess: (saved) => {
          notifySuccess({ title: `${saved.name} updated` })
          onDone()
        },
      },
    ),
  )

  return (
    <FormDialog
      open
      onOpenChange={(open) => !open && onDone()}
      title="Edit merchant"
      description="The merchant's name and photo, as they show everywhere in CREAM."
      onSubmit={onSubmit}
      footer={
        <>
          <MergeAndDeleteButton merchant={merchant} onDeleted={onDone} />
          <Button type="button" variant="outline" className="ml-auto" onClick={onDone}>
            Cancel
          </Button>
          <Button type="submit" disabled={!isDirty || update.isPending}>
            {update.isPending ? "Saving…" : "Save"}
          </Button>
        </>
      }
    >
      {update.isError && <FormAlert message={userMessage(update.error)} />}

      <div className="flex items-center gap-3">
        <MerchantLogo name={merchant.name} website={merchant.website} className="size-14 text-lg" />
        <ComingSoonButton>Choose photo</ComingSoonButton>
        <ComingSoonButton>Remove</ComingSoonButton>
      </div>

      <FormField id="merchant-name" label="Merchant name" error={errors.name?.message}>
        <Input id="merchant-name" {...fieldA11y("merchant-name", errors.name?.message)} {...register("name")} />
      </FormField>

      <FormField id="merchant-website" label="Website" error={errors.website?.message}>
        <Input
          id="merchant-website"
          placeholder="e.g. wolt.com"
          inputMode="url"
          {...fieldA11y("merchant-website", errors.website?.message)}
          {...register("website")}
        />
        <p className="text-sm text-muted-foreground">{WEBSITE_HINT}</p>
      </FormField>

      <SwitchCard
        id="merchant-recurring"
        title="Mark this merchant as recurring"
        description={RECURRING_HINT}
        checked={false}
        onCheckedChange={() => {}}
        disabled
      />
    </FormDialog>
  )
}

/** "Edit" on a merchant in Settings › Merchants. */
export function EditMerchantDialog({ merchant }: { merchant: MerchantSummary }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <Button variant="outline" size="sm" className="h-8" onClick={() => setOpen(true)}>
        <Pencil aria-hidden />
        Edit
      </Button>
      {/* Mounted only while open: every opening starts from the merchant as it is now */}
      {open && <EditMerchantForm merchant={merchant} onDone={() => setOpen(false)} />}
    </>
  )
}

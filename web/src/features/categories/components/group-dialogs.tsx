import { useState, type ReactNode } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm, useWatch } from "react-hook-form"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { FormAlert } from "@/components/form-alert"
import { FormDialog } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { notifySuccess } from "@/lib/notify"
import { useCreateCategory, useDeleteCategory, useUpdateCategory, type Category, type CategoryType } from "../api"
import { BUDGET_CHOICES, DEFAULT_BUDGET_BY, budgetHint } from "../budget"
import { groupSchema, type GroupValues } from "../schemas"

const BUDGET_LABELS = Object.fromEntries(BUDGET_CHOICES.map(({ value, label }) => [value, label]))

type GroupFormProps = {
  title: string
  defaultValues: GroupValues
  // Edit shows what the budget choice means; Create, like Monarch's, doesn't
  showHint: boolean
  isPending: boolean
  error: Error | null
  onSubmit: (values: GroupValues) => void
  open: boolean
  onOpenChange: (open: boolean) => void
  // Edit's Delete and Cancel; Create has only Save
  extraButtons?: ReactNode
}

function GroupForm({
  title,
  defaultValues,
  showHint,
  isPending,
  error,
  onSubmit,
  open,
  onOpenChange,
  extraButtons,
}: GroupFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<GroupValues>({ resolver: zodResolver(groupSchema), defaultValues })
  const budgetBy = useWatch({ control, name: "budget_by" })

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description="A group's name and how it is budgeted."
      onSubmit={handleSubmit(onSubmit)}
      footer={
        <>
          {extraButtons}
          {/* Alone on the right in Create; next to Cancel in Edit */}
          <Button type="submit" className={extraButtons ? "px-4" : "ml-auto px-4"} disabled={!isDirty || isPending}>
            {isPending ? "Saving…" : "Save"}
          </Button>
        </>
      }
    >
      {error && <FormAlert message={userMessage(error)} />}
      <FormField id="group-name" label="Name" error={errors.name?.message}>
        <Input id="group-name" className="h-10" autoFocus {...fieldA11y("group-name", errors.name?.message)} {...register("name")} />
      </FormField>
      <FormField id="group-budget" label="Budget">
        <Controller
          control={control}
          name="budget_by"
          render={({ field }) => (
            <Select items={BUDGET_LABELS} value={field.value} onValueChange={(value) => field.onChange(value)}>
              <SelectTrigger id="group-budget">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {BUDGET_CHOICES.map(({ value, label }) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {showHint && <p className="text-sm text-muted-foreground">{budgetHint(budgetBy)}</p>}
      </FormField>
    </FormDialog>
  )
}

/** "Create group" next to Income, Expenses or Transfers: a new group of that kind. */
export function CreateGroupDialog({ type, trigger }: { type: CategoryType; trigger: (open: () => void) => ReactNode }) {
  const [open, setOpen] = useState(false)
  const create = useCreateCategory()

  return (
    <>
      {trigger(() => {
        create.reset()
        setOpen(true)
      })}
      {open && (
        <GroupForm
          open={open}
          onOpenChange={setOpen}
          title="Create Group"
          defaultValues={{ name: "", budget_by: DEFAULT_BUDGET_BY }}
          showHint={false}
          isPending={create.isPending}
          error={create.error}
          onSubmit={(values) =>
            create.mutate(
              { ...values, type, is_group: true },
              {
                onSuccess: (group) => {
                  setOpen(false)
                  notifySuccess({ title: `${group.name} created` })
                },
              },
            )
          }
        />
      )}
    </>
  )
}

/** "Edit" next to a group's name: rename it, change its budget choice, or delete it with its categories. */
export function EditGroupDialog({
  group,
  categoryCount,
  trigger,
}: {
  group: Category
  categoryCount: number
  trigger: (open: () => void) => ReactNode
}) {
  const [open, setOpen] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const update = useUpdateCategory()
  const remove = useDeleteCategory()

  return (
    <>
      {trigger(() => {
        update.reset()
        setOpen(true)
      })}
      {open && (
        <GroupForm
          open={open}
          onOpenChange={setOpen}
          title="Edit Group"
          defaultValues={{ name: group.name, budget_by: group.budget_by ?? DEFAULT_BUDGET_BY }}
          showHint
          isPending={update.isPending}
          error={update.error}
          onSubmit={(values) =>
            update.mutate(
              { id: group.id, changes: values },
              {
                onSuccess: () => {
                  setOpen(false)
                  notifySuccess({ title: "Group updated" })
                },
              },
            )
          }
          extraButtons={
            <>
              <Button
                type="button"
                variant="outline"
                className="px-4 text-destructive hover:text-destructive"
                onClick={() => {
                  remove.reset()
                  setConfirmingDelete(true)
                }}
              >
                Delete
              </Button>
              <Button type="button" variant="outline" className="ml-auto px-4" onClick={() => setOpen(false)}>
                Cancel
              </Button>
            </>
          }
        />
      )}
      <ConfirmDialog
        open={confirmingDelete}
        onOpenChange={setConfirmingDelete}
        title={`Delete ${group.name}?`}
        description={
          categoryCount > 0
            ? `Its ${categoryCount === 1 ? "category" : `${categoryCount} categories`} will be deleted too. Groups and categories that hold transactions can't be deleted.`
            : "The group is empty, so nothing else changes."
        }
        confirmLabel="Delete"
        confirmVariant="destructive"
        isPending={remove.isPending}
        errorMessage={remove.isError ? userMessage(remove.error) : undefined}
        onConfirm={() =>
          remove.mutate(group.id, {
            onSuccess: () => {
              setConfirmingDelete(false)
              setOpen(false)
              notifySuccess({ title: `${group.name} deleted` })
            },
          })
        }
      />
    </>
  )
}

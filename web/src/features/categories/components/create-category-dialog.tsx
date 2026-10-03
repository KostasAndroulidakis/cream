import { useState, type ReactNode } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { Controller, useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormDialog } from "@/components/form-dialog"
import { FormField } from "@/components/form-field"
import { SwitchCard } from "@/components/switch-card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { notifySuccess } from "@/lib/notify"
import { categoriesQueryOptions, useCreateCategory, type Category, type CategoryType } from "../api"
import { categorySchema, type CategoryValues } from "../schemas"
import { EmojiPicker } from "./emoji-picker"

// Shown in the icon button until an emoji is picked; saved as no icon
const NO_ICON = "❓"

// Monarch lists expense groups first, then income, then transfers
const GROUP_SECTIONS: readonly { type: CategoryType; label: string }[] = [
  { type: "expense", label: "Expense" },
  { type: "income", label: "Income" },
  { type: "transfer", label: "Transfer" },
]

function GroupPicker({
  groups,
  value,
  onChange,
}: {
  groups: Category[]
  value: number | undefined
  onChange: (id: number) => void
}) {
  const labels = Object.fromEntries(groups.map((group) => [String(group.id), group.name]))
  return (
    <Select
      items={labels}
      value={value === undefined ? null : String(value)}
      onValueChange={(next) => next !== null && onChange(Number(next))}
    >
      <SelectTrigger id="category-group">
        <SelectValue placeholder="Pick a group" />
      </SelectTrigger>
      <SelectContent className="max-h-80">
        {GROUP_SECTIONS.map(({ type, label }) => {
          const ofType = groups.filter((group) => group.type === type)
          if (ofType.length === 0) return null
          return (
            <SelectGroup key={type} label={label}>
              {ofType.map((group) => (
                <SelectItem key={group.id} value={String(group.id)}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectGroup>
          )
        })}
      </SelectContent>
    </Select>
  )
}

function CreateCategoryForm({ groupId, onDone }: { groupId: number; onDone: () => void }) {
  const { data: categories = [] } = useQuery(categoriesQueryOptions)
  const groups = categories.filter((category) => category.is_group)
  const create = useCreateCategory()
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<CategoryValues>({
    resolver: zodResolver(categorySchema),
    defaultValues: { icon: null, name: "", group_id: groupId, exclude_from_budget: false },
  })

  const onSubmit = handleSubmit(({ group_id, ...values }) => {
    const group = groups.find((candidate) => candidate.id === group_id)
    if (!group) return
    create.mutate(
      // A category takes its group's kind (income, expense or transfer)
      { ...values, parent_id: group_id, type: group.type },
      {
        onSuccess: (category) => {
          onDone()
          notifySuccess({ title: `${category.name} created` })
        },
      },
    )
  })

  return (
    <FormDialog
      open
      onOpenChange={(open) => !open && onDone()}
      title="Create Category"
      description="A new category: its icon, name, group and whether it counts in the budget."
      onSubmit={onSubmit}
      footer={
        <Button type="submit" className="ml-auto px-4" disabled={create.isPending}>
          {create.isPending ? "Saving…" : "Save"}
        </Button>
      }
    >
      {create.isError && <FormAlert message={userMessage(create.error)} />}

      <FormField id="category-name" label="Icon & Name" error={errors.name?.message}>
        <div className="flex h-10 overflow-hidden rounded-lg border border-input focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50 has-aria-invalid:border-destructive">
          <Controller
            control={control}
            name="icon"
            render={({ field }) => (
              <EmojiPicker value={field.value} onChange={field.onChange} placeholder={NO_ICON} className="border-r" />
            )}
          />
          <input
            id="category-name"
            placeholder="New Category"
            autoFocus
            className="min-w-0 flex-1 bg-transparent px-3 text-base outline-none placeholder:text-muted-foreground md:text-sm"
            {...fieldA11y("category-name", errors.name?.message)}
            {...register("name")}
          />
        </div>
      </FormField>

      <FormField id="category-group" label="Group" error={errors.group_id?.message}>
        <Controller
          control={control}
          name="group_id"
          render={({ field }) => <GroupPicker groups={groups} value={field.value} onChange={field.onChange} />}
        />
      </FormField>

      <Controller
        control={control}
        name="exclude_from_budget"
        render={({ field }) => (
          <SwitchCard
            id="category-exclude"
            title="Exclude this category from the budget"
            description="This category and any transactions linked to it will be hidden from your budget."
            checked={field.value}
            onCheckedChange={field.onChange}
          />
        )}
      />
    </FormDialog>
  )
}

/** "Create Category" under a group: a new category in that group (another can be picked). */
export function CreateCategoryDialog({
  groupId,
  trigger,
}: {
  groupId: number
  trigger: (open: () => void) => ReactNode
}) {
  const [open, setOpen] = useState(false)
  return (
    <>
      {trigger(() => setOpen(true))}
      {/* Mounted only while open, so every opening starts from a fresh form */}
      {open && <CreateCategoryForm groupId={groupId} onDone={() => setOpen(false)} />}
    </>
  )
}

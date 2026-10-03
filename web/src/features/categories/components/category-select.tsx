import type { ComponentProps } from "react"

import { NativeSelect } from "@/components/native-select"
import { NO_CATEGORY, type CategoryGroup } from "../grouping"

type CategorySelectProps = Omit<ComponentProps<"select">, "children"> & {
  groups: CategoryGroup[]
  // The empty choice: a prompt that can't be picked again, or a real "No change" option
  emptyOption?: { label: string; selectable: boolean }
}

const PICK_PROMPT = { label: "Pick a category", selectable: false }

/** A category picker with categories under their groups and an empty first choice. */
export function CategorySelect({ groups, emptyOption = PICK_PROMPT, ...props }: CategorySelectProps) {
  return (
    <NativeSelect {...props}>
      <option value={NO_CATEGORY} disabled={!emptyOption.selectable}>
        {emptyOption.label}
      </option>
      {groups.map((group) => (
        <optgroup key={group.label} label={group.label}>
          {group.categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </optgroup>
      ))}
    </NativeSelect>
  )
}

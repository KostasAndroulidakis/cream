import type { ComponentProps } from "react"

import { NativeSelect } from "@/components/native-select"
import { NO_CATEGORY, type CategoryGroup } from "../grouping"

type CategorySelectProps = Omit<ComponentProps<"select">, "children"> & {
  groups: CategoryGroup[]
}

/** A category picker with categories under their groups and an empty "Pick a category" start. */
export function CategorySelect({ groups, ...props }: CategorySelectProps) {
  return (
    <NativeSelect {...props}>
      <option value={NO_CATEGORY} disabled>
        Pick a category
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

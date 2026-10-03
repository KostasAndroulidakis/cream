import { useQuery } from "@tanstack/react-query"
import { Info } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { categoriesQueryOptions } from "../api"
import { categorySections, type CategoryGroupBlock, type CategorySection } from "../settings-sections"
import { CreateCategoryDialog } from "./create-category-dialog"
import { CreateGroupDialog, EditGroupDialog } from "./group-dialogs"
import { SortableCategoryList } from "./sortable-category-list"

// Name of the block for categories that belong to no group
const UNGROUPED_TITLE = "My categories"

/** Monarch's small text actions ("Edit", "Create Category", "Create group"). */
function TextAction({ children, className, onClick }: { children: string; className?: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn("rounded-sm text-xs font-medium hover:underline focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none", className)}
    >
      {children}
    </button>
  )
}

function GroupBlock({ block: { group, categories } }: { block: CategoryGroupBlock }) {
  const title = group?.name ?? UNGROUPED_TITLE
  return (
    <section aria-label={title} className="rounded-lg bg-muted/70 p-2">
      <div className="flex items-center gap-2 px-1 pt-1 pb-2">
        <h4 className="text-sm font-medium">{title}</h4>
        {group && (
          <EditGroupDialog
            group={group}
            categoryCount={categories.length}
            trigger={(open) => (
              <TextAction className="text-muted-foreground" onClick={open}>
                Edit
              </TextAction>
            )}
          />
        )}
      </div>
      {categories.length > 0 ? (
        <SortableCategoryList categories={categories} />
      ) : (
        <p className="px-1 text-sm text-muted-foreground">No categories in this group yet.</p>
      )}
      {/* The user's ungrouped categories have no group to add to */}
      {group && (
        <div className="px-1 pt-2">
          <CreateCategoryDialog
            groupId={group.id}
            trigger={(open) => (
              <TextAction className="text-muted-foreground" onClick={open}>
                Create Category
              </TextAction>
            )}
          />
        </div>
      )}
    </section>
  )
}

function Section({ section }: { section: CategorySection }) {
  const headingId = `categories-${section.type}`
  return (
    <section aria-labelledby={headingId} className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 id={headingId} className="font-medium">
          {section.title}
        </h3>
        <CreateGroupDialog
          type={section.type}
          trigger={(open) => (
            <TextAction className="text-primary" onClick={open}>
              Create group
            </TextAction>
          )}
        />
      </div>
      <div className="space-y-3">
        {section.groups.map((block) => (
          <GroupBlock key={block.group?.id ?? "ungrouped"} block={block} />
        ))}
      </div>
    </section>
  )
}

/** Settings › Categories: every group with its categories, reorderable by drag and drop. */
export function CategorySettings() {
  const categories = useQuery(categoriesQueryOptions)

  if (categories.isPending) {
    return <div className="h-96 animate-pulse rounded-lg bg-muted" aria-label="Loading categories" />
  }
  if (categories.isError) return <FormAlert message={userMessage(categories.error)} />

  return (
    <div className="space-y-6">
      <p className="flex items-start gap-2 rounded-lg bg-sky-50 px-3 py-2 text-sm text-sky-900 dark:bg-sky-950 dark:text-sky-200">
        <Info className="mt-0.5 size-4 shrink-0" aria-hidden />
        Changes you make to your groups and categories here apply everywhere in CREAM. Drag a category to change
        its place in its group.
      </p>
      {categorySections(categories.data).map((section) => (
        <Section key={section.type} section={section} />
      ))}
    </div>
  )
}

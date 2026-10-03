import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core"
import { SortableContext, arrayMove, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { GripVertical } from "lucide-react"

import { userMessage } from "@/lib/api/errors"
import { notifyError } from "@/lib/notify"
import { cn } from "@/lib/utils"
import { useReorderCategories, type Category } from "../api"

// A click (e.g. to open the category later) only becomes a drag after the pointer moves this far
const DRAG_DISTANCE_PX = 4
// Shown for categories that have no emoji
const DEFAULT_ICON = "•"

function CategoryRow({ category }: { category: Category }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: category.id })

  return (
    <li
      ref={setNodeRef}
      // Up and down only: the row never drifts out of its group sideways
      style={{ transform: CSS.Translate.toString(transform && { ...transform, x: 0 }), transition }}
      className={cn(
        "flex h-9 cursor-grab touch-none items-center gap-2 rounded-md border bg-card px-2 text-sm select-none",
        "focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none",
        isDragging && "relative z-10 cursor-grabbing shadow-md",
      )}
      {...attributes}
      {...listeners}
    >
      <GripVertical className="size-4 shrink-0 text-muted-foreground/60" aria-hidden />
      <span aria-hidden className="w-5 text-center">
        {category.icon ?? DEFAULT_ICON}
      </span>
      <span className="truncate">{category.name}</span>
    </li>
  )
}

/** One group's categories; drag a row (or focus it and use space and the arrow keys) to reorder them. */
export function SortableCategoryList({ categories }: { categories: Category[] }) {
  const reorder = useReorderCategories()
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: DRAG_DISTANCE_PX } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )
  const ids = categories.map((category) => category.id)

  function onDragEnd({ active, over }: DragEndEvent) {
    if (!over || active.id === over.id) return
    const next = arrayMove(ids, ids.indexOf(Number(active.id)), ids.indexOf(Number(over.id)))
    reorder.mutate(next, { onError: (error) => notifyError(userMessage(error)) })
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <ul className="flex flex-col gap-1">
          {categories.map((category) => (
            <CategoryRow key={category.id} category={category} />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  )
}

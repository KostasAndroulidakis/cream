import { CategorySettings } from "@/features/categories/components/category-settings"

/** Settings › Categories, like Monarch's. */
export function SettingsCategoriesPage() {
  return (
    <section aria-labelledby="categories-heading" className="rounded-xl border bg-card shadow-xs">
      <h2 id="categories-heading" className="border-b px-6 py-4 text-lg font-medium tracking-tight">
        Categories
      </h2>
      <div className="px-6 py-5">
        <CategorySettings />
      </div>
    </section>
  )
}

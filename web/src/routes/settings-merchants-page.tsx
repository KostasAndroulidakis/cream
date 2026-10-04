import { MerchantList } from "@/features/merchants/components/merchant-list"

/** Settings › Merchants, like Monarch's. */
export function SettingsMerchantsPage() {
  return (
    <section aria-labelledby="merchants-heading" className="rounded-xl border bg-card shadow-xs">
      <h2 id="merchants-heading" className="border-b px-6 py-4 text-lg font-medium tracking-tight">
        Merchants
      </h2>
      <div className="space-y-5 px-6 py-5">
        <p>
          These are all of the different merchants you have interacted with in your transaction history. You can edit
          how a merchant displays throughout CREAM, and delete merchants you're not using.
        </p>
        <MerchantList />
        {/* Logo.dev's free plan asks for this link wherever its logos show */}
        <p className="text-sm text-muted-foreground">
          <a href="https://logo.dev" target="_blank" rel="noreferrer" className="underline underline-offset-2">
            Logos provided by Logo.dev
          </a>
        </p>
      </div>
    </section>
  )
}

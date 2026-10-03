import type { AccountClass, WalletType } from "../../api"
import { useAccountTypes } from "../../use-account-types"
import { ACCOUNT_TYPE_ICONS } from "../../wallet-types"

const CLASS_HEADINGS: Record<AccountClass, string> = { asset: "Asset", liability: "Liability" }

/** "Add Manual Account": the account types under Asset and Liability, in Monarch's order. */
export function ManualTypesStep({ onPick }: { onPick: (type: WalletType) => void }) {
  const { catalog } = useAccountTypes()

  return (
    <div className="pb-2">
      {(Object.keys(CLASS_HEADINGS) as AccountClass[]).map((accountClass) => (
        <section key={accountClass} aria-label={CLASS_HEADINGS[accountClass]}>
          <h3 className="bg-muted/60 px-6 py-2.5 text-sm text-muted-foreground">{CLASS_HEADINGS[accountClass]}</h3>
          <ul className="divide-y">
            {catalog
              .filter((info) => info.account_class === accountClass)
              .map(({ type, label }) => {
                const Icon = ACCOUNT_TYPE_ICONS[type]
                return (
                  <li key={type}>
                    <button
                      type="button"
                      onClick={() => onPick(type)}
                      className="flex w-full items-center gap-4 px-6 py-3.5 text-left text-base hover:bg-muted/60"
                    >
                      <Icon className="size-[1.125rem]" aria-hidden />
                      {label}
                    </button>
                  </li>
                )
              })}
          </ul>
        </section>
      ))}
    </div>
  )
}

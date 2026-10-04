import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Pencil, Search } from "lucide-react"

import { ComingSoonButton } from "@/components/coming-soon-button"
import { FormAlert } from "@/components/form-alert"
import { ListSkeleton } from "@/components/list-skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { userMessage } from "@/lib/api/errors"
import { pluralize } from "@/lib/text"
import { merchantsQueryOptions, type MerchantOrder, type MerchantSummary } from "../api"
import { MERCHANT_ORDERS } from "../order"
import { useMerchantOrder } from "../use-merchant-order"
import { MerchantAvatar } from "./merchant-avatar"

const SKELETON_ROWS = 6
const ROW_HEIGHT = "h-[4.25rem]"

/** One merchant: its mark, name and how many transactions it has, with Edit on the right. */
function MerchantRow({ merchant }: { merchant: MerchantSummary }) {
  return (
    <li className="flex items-center gap-4 py-3">
      <MerchantAvatar name={merchant.name} className="size-10 text-sm" />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{merchant.name}</p>
        <p className="text-sm text-muted-foreground">{pluralize(merchant.transaction_count, "transaction")}</p>
      </div>
      <ComingSoonButton icon={Pencil} className="h-8">
        Edit
      </ComingSoonButton>
    </li>
  )
}

/** Shown when there's nothing to list: no merchants yet, or none matching the search. */
function NoMerchants({ query }: { query: string }) {
  return (
    <div className="py-10 text-center">
      <p className="font-semibold">No merchants found</p>
      <p className="mx-auto mt-1 max-w-56 text-muted-foreground">
        {query ? `No merchant matches “${query}”.` : "You don't have merchants assigned to transactions yet."}
      </p>
    </div>
  )
}

/** Settings › Merchants: every merchant with transactions, sorted and searchable, like Monarch's. */
export function MerchantList() {
  const [order, setOrder] = useMerchantOrder()
  const [query, setQuery] = useState("")
  const { data: merchants, isPending, isError, error } = useQuery(merchantsQueryOptions(order))
  const needle = query.trim().toLowerCase()
  const shown = merchants?.filter((merchant) => merchant.name.toLowerCase().includes(needle)) ?? []

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Select
          items={MERCHANT_ORDERS}
          value={order}
          // The items are exactly the orders
          onValueChange={(value) => setOrder(value as MerchantOrder)}
        >
          <SelectTrigger aria-label="Sort merchants" className="h-9 w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(MERCHANT_ORDERS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <label className="flex h-9 w-full items-center gap-2 rounded-lg border px-3 focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50 sm:w-64">
          <Search className="size-4 shrink-0 text-muted-foreground" aria-hidden />
          <input
            type="search"
            aria-label="Search merchants"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={merchants?.length ? `Search ${merchants.length} merchants…` : "Search for a merchant…"}
            className="min-w-0 flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
          />
        </label>
      </div>

      {isError && <FormAlert message={userMessage(error)} />}
      {isPending ? (
        <ListSkeleton rows={SKELETON_ROWS} label="Loading merchants" rowClassName={ROW_HEIGHT} />
      ) : shown.length === 0 ? (
        <NoMerchants query={query.trim()} />
      ) : (
        <section aria-labelledby="merchant-count">
          <h3 id="merchant-count" className="pb-1 text-lg font-semibold">
            {pluralize(shown.length, "Merchant")}
          </h3>
          <ul className="divide-y">
            {shown.map((merchant) => (
              <MerchantRow key={merchant.id} merchant={merchant} />
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

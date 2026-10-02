import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { cn } from "@/lib/utils"
import { connectionsQueryOptions, useDeleteConnection, type BankAccount, type BankConnection } from "../api"
import { countryName } from "../countries"
import { LinkAccountControl } from "./link-account-control"

const DATE_FORMAT = new Intl.DateTimeFormat(undefined, { dateStyle: "medium" })
const DATE_TIME_FORMAT = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" })

const STATUS_STYLES: Record<BankConnection["status"], { label: string; className: string }> = {
  active: { label: "Connected", className: "bg-primary/10 text-primary" },
  expired: { label: "Access expired", className: "bg-destructive/10 text-destructive" },
  pending: { label: "Waiting for bank", className: "bg-muted text-muted-foreground" },
}

function AccountRow({ account, walletName }: { account: BankAccount; walletName?: string }) {
  return (
    <li className="flex flex-wrap items-center justify-between gap-3 py-3">
      <div className="min-w-0">
        <p className="font-medium">
          {account.name}
          {account.iban_last4 && <span className="text-muted-foreground"> ••{account.iban_last4}</span>}
        </p>
        <p className="text-sm text-muted-foreground">
          {account.currency}
          {account.last_synced_at
            ? `, last synced ${DATE_TIME_FORMAT.format(new Date(account.last_synced_at))}`
            : ", not synced yet"}
        </p>
      </div>
      {walletName ? (
        <p className="text-sm">
          Goes to <span className="font-medium">{walletName}</span>
        </p>
      ) : (
        <LinkAccountControl account={account} />
      )}
    </li>
  )
}

function ConnectionCard({ connection, walletNames }: { connection: BankConnection; walletNames: Map<number, string> }) {
  const deleteConnection = useDeleteConnection()
  const { label, className } = STATUS_STYLES[connection.status]

  return (
    <section className="rounded-xl border bg-card px-6 py-5 shadow-xs">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold tracking-tight">{connection.aspsp_name}</h3>
          <p className="text-sm text-muted-foreground">
            {countryName(connection.aspsp_country)}
            {connection.valid_until && `, access until ${DATE_FORMAT.format(new Date(connection.valid_until))}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", className)}>{label}</span>
          <Button
            variant="ghost"
            size="sm"
            disabled={deleteConnection.isPending}
            onClick={() => deleteConnection.mutate(connection.id)}
          >
            Disconnect
          </Button>
        </div>
      </header>
      {deleteConnection.isError && <FormAlert message={userMessage(deleteConnection.error)} />}
      <ul className="mt-2 divide-y">
        {connection.accounts.map((account) => (
          <AccountRow
            key={account.id}
            account={account}
            walletName={account.wallet_id === null ? undefined : walletNames.get(account.wallet_id)}
          />
        ))}
      </ul>
    </section>
  )
}

export function ConnectionList() {
  const connections = useQuery(connectionsQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)

  if (connections.isPending) return <div className="h-32 animate-pulse rounded-xl bg-muted" aria-label="Loading connections" />
  if (connections.isError) return <FormAlert message={userMessage(connections.error)} />
  if (connections.data.length === 0) {
    return <p className="text-sm text-muted-foreground">No banks connected yet.</p>
  }

  const walletNames = new Map(wallets.map((wallet) => [wallet.id, wallet.name]))
  return (
    <div className="space-y-4">
      {connections.data.map((connection) => (
        <ConnectionCard key={connection.id} connection={connection} walletNames={walletNames} />
      ))}
    </div>
  )
}

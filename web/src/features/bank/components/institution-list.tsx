import { useQuery } from "@tanstack/react-query"
import { ArrowRight } from "lucide-react"

import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { walletsQueryOptions } from "@/features/wallets/api"
import { userMessage } from "@/lib/api/errors"
import { formatNumericDate, timeAgo } from "@/lib/dates"
import { pluralize } from "@/lib/text"
import { cn } from "@/lib/utils"
import { connectionsQueryOptions, useStartConnection, type BankAccount, type BankConnection } from "../api"
import { DisconnectMenu } from "./disconnect-menu"
import { LinkAccountControl } from "./link-account-control"

// The service CREAM reaches banks through, where Monarch names Plaid or MX
const PROVIDER = "Enable Banking"

function InstitutionAvatar({ name }: { name: string }) {
  return (
    <span
      aria-hidden
      className="inline-grid size-10 shrink-0 place-items-center rounded-full bg-muted text-base font-semibold text-muted-foreground"
    >
      {name.charAt(0).toUpperCase()}
    </span>
  )
}

/** The most recent sync of any of the connection's accounts. */
function lastSynced(connection: BankConnection): string | null {
  const times = connection.accounts.map((account) => account.last_synced_at).filter((time) => time !== null)
  return times.length > 0 ? times.reduce((latest, time) => (time > latest ? time : latest)) : null
}

function syncStatus(connection: BankConnection): { text: string; problem: boolean } {
  if (connection.status === "expired") return { text: "Access expired. Update to reconnect", problem: true }
  if (connection.status === "pending") return { text: "Waiting for the bank", problem: false }
  const synced = lastSynced(connection)
  return { text: synced ? `Synced with institution ${timeAgo(synced)}` : "Not synced yet", problem: false }
}

/** "Update": logs in at the bank again, for a connection whose access ran out. */
function ReconnectButton({ connection }: { connection: BankConnection }) {
  const reconnect = useStartConnection()
  return (
    <Button
      disabled={reconnect.isPending}
      onClick={() => reconnect.mutate({ aspsp_name: connection.aspsp_name, country: connection.aspsp_country })}
    >
      {reconnect.isPending ? "Opening your bank…" : "Update"}
    </Button>
  )
}

function AccountRow({ account, walletName }: { account: BankAccount; walletName?: string }) {
  return (
    <li className="grid grid-cols-1 items-center gap-3 py-4 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
      <div className="min-w-0">
        <p className="truncate font-medium">{account.name}</p>
        <p className="text-sm text-muted-foreground">
          {account.currency}
          {account.iban_last4 && ` ${account.iban_last4}`}
        </p>
        <p className="text-sm text-muted-foreground">Added to CREAM on {formatNumericDate(account.created_at)}</p>
      </div>
      <div className="min-w-0">
        {walletName ? (
          <p className="flex items-center gap-2 text-sm">
            <ArrowRight className="size-4 text-muted-foreground" aria-hidden />
            <span className="truncate font-medium">{walletName}</span>
          </p>
        ) : (
          <LinkAccountControl account={account} />
        )}
      </div>
      <p className="text-sm text-muted-foreground md:text-right">
        {account.last_synced_at ? `CREAM synced ${timeAgo(account.last_synced_at)}` : "Not synced yet"}
      </p>
    </li>
  )
}

function InstitutionCard({ connection, walletNames }: { connection: BankConnection; walletNames: Map<number, string> }) {
  const status = syncStatus(connection)

  return (
    <section
      aria-label={connection.aspsp_name}
      className="rounded-xl border bg-card px-6 py-5 shadow-xs"
    >
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-4">
          <InstitutionAvatar name={connection.aspsp_name} />
          <div className="min-w-0">
            <h3 className="truncate text-lg font-semibold tracking-tight">{connection.aspsp_name}</h3>
            <p className="text-sm text-muted-foreground">Connected {formatNumericDate(connection.created_at)}</p>
            <p className="text-sm text-muted-foreground">{pluralize(connection.accounts.length, "account")}</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="max-w-64 text-sm">
            <p className="font-medium">{PROVIDER}</p>
            <p className={cn(status.problem ? "text-destructive" : "text-muted-foreground")}>{status.text}</p>
          </div>
          <DisconnectMenu connection={connection} />
          {connection.status === "expired" && <ReconnectButton connection={connection} />}
        </div>
      </header>
      {connection.accounts.length > 0 && (
        <ul className="mt-2 divide-y">
          {connection.accounts.map((account) => (
            <AccountRow
              key={account.id}
              account={account}
              walletName={account.wallet_id === null ? undefined : walletNames.get(account.wallet_id)}
            />
          ))}
        </ul>
      )}
    </section>
  )
}

/** One card per connected bank, with its accounts; nothing at all when none is connected, like Monarch. */
export function InstitutionList() {
  const connections = useQuery(connectionsQueryOptions)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)

  if (connections.isPending) {
    return <div className="h-40 animate-pulse rounded-xl bg-muted" aria-label="Loading institutions" />
  }
  if (connections.isError) return <FormAlert message={userMessage(connections.error)} />

  const walletNames = new Map(wallets.map((wallet) => [wallet.id, wallet.name]))
  return connections.data.map((connection) => (
    <InstitutionCard key={connection.id} connection={connection} walletNames={walletNames} />
  ))
}

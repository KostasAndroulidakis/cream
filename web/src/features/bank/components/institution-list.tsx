import { useQuery } from "@tanstack/react-query"

import { COMING_SOON } from "@/components/coming-soon-button"
import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { walletsQueryOptions, type Wallet } from "@/features/wallets/api"
import { EditAccountDialog } from "@/features/wallets/components/edit-account-dialog"
import { useAccountTypes } from "@/features/wallets/use-account-types"
import { userMessage } from "@/lib/api/errors"
import { timeAgo } from "@/lib/dates"
import { cn } from "@/lib/utils"
import {
  aspspsQueryOptions,
  connectionsQueryOptions,
  useStartConnection,
  type BankAccount,
  type BankConnection,
} from "../api"
import { DisconnectMenu } from "./disconnect-menu"
import { LinkAccountControl } from "./link-account-control"

// The service CREAM reaches banks through, where Monarch names Plaid or MX
const PROVIDER = "Enable Banking"

/** The bank's logo from the provider's list of banks, or its initial while that loads or has none. */
function InstitutionLogo({ connection, className }: { connection: BankConnection; className?: string }) {
  const { data: banks } = useQuery(aspspsQueryOptions(connection.aspsp_country))
  const logo = banks?.find((bank) => bank.name === connection.aspsp_name)?.logo

  if (logo) return <img src={logo} alt="" className={cn("size-8 shrink-0 rounded-full object-contain", className)} />
  return (
    <span
      aria-hidden
      className={cn(
        "inline-grid size-8 shrink-0 place-items-center rounded-full bg-muted text-sm font-semibold text-muted-foreground",
        className,
      )}
    >
      {connection.aspsp_name.charAt(0).toUpperCase()}
    </span>
  )
}

/** The most recent sync of any of the connection's accounts. */
function lastSynced(connection: BankConnection): string | null {
  const times = connection.accounts.map((account) => account.last_synced_at).filter((time) => time !== null)
  return times.length > 0 ? times.reduce((latest, time) => (time > latest ? time : latest)) : null
}

/** Monarch's small line above the name, e.g. "PLAID • LAST UPDATE 1 MONTH AGO". */
function statusLine(connection: BankConnection): { text: string; problem: boolean } {
  if (connection.status === "expired") return { text: "Access expired", problem: true }
  if (connection.status === "pending") return { text: "Waiting for the bank", problem: false }
  const synced = lastSynced(connection)
  return { text: synced ? `Last update ${timeAgo(synced)}` : "Not synced yet", problem: false }
}

/** "Update": logs in at the bank again, for a connection whose access ran out. */
function ReconnectButton({ connection }: { connection: BankConnection }) {
  const reconnect = useStartConnection()
  return (
    <Button
      size="sm"
      disabled={reconnect.isPending}
      onClick={() => reconnect.mutate({ aspsp_name: connection.aspsp_name, country: connection.aspsp_country })}
    >
      {reconnect.isPending ? "Opening your bank…" : "Update"}
    </Button>
  )
}

/** Monarch's "View"; account pages come later, so for now it only says so. */
function AccountButton({ children }: { children: string }) {
  return (
    <Button
      variant="outline"
      size="sm"
      aria-disabled
      title={COMING_SOON}
      className="cursor-not-allowed hover:bg-background active:not-aria-[haspopup]:translate-y-0"
    >
      {children}
    </Button>
  )
}

function AccountRow({
  account,
  wallet,
  connection,
}: {
  account: BankAccount
  wallet?: Wallet
  connection: BankConnection
}) {
  const { subtypeLabel } = useAccountTypes()

  return (
    <li className="flex flex-wrap items-center justify-between gap-3 py-3.5">
      <div className="min-w-0">
        <p className="truncate text-[0.9375rem]">{account.name}</p>
        <p className="text-sm text-muted-foreground">
          {wallet ? subtypeLabel(wallet.type, wallet.subtype) : "Not linked to a CREAM account yet"}
        </p>
      </div>
      {wallet ? (
        <div className="flex items-center gap-2">
          <AccountButton>View</AccountButton>
          <EditAccountDialog
            wallet={wallet}
            logo={<InstitutionLogo connection={connection} className="size-12 text-lg" />}
            trigger={(open) => (
              <Button variant="outline" size="sm" onClick={open}>
                Edit
              </Button>
            )}
          />
        </div>
      ) : (
        // Monarch adds every account on its own; CREAM asks where the transactions go
        <LinkAccountControl account={account} />
      )}
    </li>
  )
}

function InstitutionCard({ connection, wallets }: { connection: BankConnection; wallets: Map<number, Wallet> }) {
  const status = statusLine(connection)

  return (
    <section aria-label={connection.aspsp_name} className="rounded-xl border bg-card px-5 py-4 shadow-xs">
      <header className="flex items-center justify-between gap-4 pb-2">
        <div className="flex min-w-0 items-center gap-3">
          <InstitutionLogo connection={connection} />
          <div className="min-w-0">
            <p
              className={cn(
                "text-[0.6875rem] font-medium tracking-wide uppercase",
                status.problem ? "text-destructive" : "text-muted-foreground",
              )}
            >
              {PROVIDER} • {status.text}
            </p>
            <h3 className="truncate text-base font-semibold">{connection.aspsp_name}</h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {connection.status === "expired" && <ReconnectButton connection={connection} />}
          <DisconnectMenu connection={connection} />
        </div>
      </header>
      {connection.accounts.length > 0 && (
        <ul className="divide-y divide-border/60">
          {connection.accounts.map((account) => (
            <AccountRow
              key={account.id}
              account={account}
              wallet={account.wallet_id === null ? undefined : wallets.get(account.wallet_id)}
              connection={connection}
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
  const { data: walletList = [] } = useQuery(walletsQueryOptions)

  if (connections.isPending) {
    return <div className="h-40 animate-pulse rounded-xl bg-muted" aria-label="Loading institutions" />
  }
  if (connections.isError) return <FormAlert message={userMessage(connections.error)} />

  const wallets = new Map(walletList.map((wallet) => [wallet.id, wallet]))
  return connections.data.map((connection) => (
    <InstitutionCard key={connection.id} connection={connection} wallets={wallets} />
  ))
}

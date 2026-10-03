import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { walletsQueryOptions } from "@/features/wallets/api"
import { connectionsQueryOptions, useLinkAccount, type BankAccount } from "../api"

const NEW_WALLET = "new"

/** Pick where an account's transactions go: a new wallet, or an unlinked wallet in the same currency. */
export function LinkAccountControl({ account }: { account: BankAccount }) {
  const [choice, setChoice] = useState(NEW_WALLET)
  const { data: wallets = [] } = useQuery(walletsQueryOptions)
  const { data: connections = [] } = useQuery(connectionsQueryOptions)
  const linkAccount = useLinkAccount()

  const linkedWalletIds = new Set(
    connections.flatMap((connection) => connection.accounts.map((a) => a.wallet_id)).filter((id) => id !== null),
  )
  const candidates = wallets.filter((w) => w.currency === account.currency && !linkedWalletIds.has(w.id))

  // The API says which accounts CREAM can take (EUR only for now)
  if (!account.can_link) {
    return <p className="text-sm text-muted-foreground">{account.currency} accounts can't be linked yet.</p>
  }

  return (
    <div className="flex items-center gap-2">
      <NativeSelect
        aria-label={`CREAM account for ${account.name}`}
        value={choice}
        onChange={(event) => setChoice(event.target.value)}
        className="min-w-44"
      >
        <option value={NEW_WALLET}>New account</option>
        {candidates.map((wallet) => (
          <option key={wallet.id} value={wallet.id}>
            {wallet.name}
          </option>
        ))}
      </NativeSelect>
      <Button
        variant="outline"
        disabled={linkAccount.isPending}
        onClick={() =>
          linkAccount.mutate({ accountId: account.id, walletId: choice === NEW_WALLET ? null : Number(choice) })
        }
      >
        {linkAccount.isPending ? "Linking…" : "Link"}
      </Button>
    </div>
  )
}

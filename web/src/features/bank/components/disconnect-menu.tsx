import { useState } from "react"
import { Ellipsis, Unplug } from "lucide-react"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { userMessage } from "@/lib/api/errors"
import { useDeleteConnection, type BankConnection } from "../api"

/** The "…" menu of an institution, with Disconnect behind a confirmation. */
export function DisconnectMenu({ connection }: { connection: BankConnection }) {
  const [confirming, setConfirming] = useState(false)
  const deleteConnection = useDeleteConnection()

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger
          render={<Button variant="ghost" size="icon" aria-label={`More for ${connection.aspsp_name}`} />}
        >
          <Ellipsis aria-hidden />
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem
            variant="destructive"
            onClick={() => {
              deleteConnection.reset()
              setConfirming(true)
            }}
          >
            <Unplug aria-hidden />
            Disconnect
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <ConfirmDialog
        open={confirming}
        onOpenChange={setConfirming}
        title={`Disconnect ${connection.aspsp_name}?`}
        description="Its accounts and the transactions already imported stay in CREAM; new ones stop arriving."
        confirmLabel="Disconnect"
        confirmVariant="destructive"
        isPending={deleteConnection.isPending}
        errorMessage={deleteConnection.isError ? userMessage(deleteConnection.error) : undefined}
        onConfirm={() => deleteConnection.mutate(connection.id, { onSuccess: () => setConfirming(false) })}
      />
    </>
  )
}

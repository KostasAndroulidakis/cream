import { AddAccountDialog } from "./add-account/add-account-dialog"

/** What a list of accounts shows before there are any. */
export function NoAccounts() {
  return (
    <div className="rounded-xl border border-dashed px-6 py-10 text-center">
      <p className="font-medium">No accounts yet</p>
      <p className="mx-auto mt-1 max-w-xs text-sm text-muted-foreground">
        Add your bank account, the cash in your pocket, or a stash to start tracking.
      </p>
      <div className="mt-5">
        <AddAccountDialog />
      </div>
    </div>
  )
}

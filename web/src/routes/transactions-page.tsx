import { CreateTransactionDialog } from "@/features/transactions/components/create-transaction-dialog"
import { TransactionsList } from "@/features/transactions/components/transactions-list"

export function TransactionsPage() {
  return (
    <div className="space-y-4">
      <header className="flex min-h-10 flex-wrap items-center justify-between gap-4">
        <h1 className="text-xl font-semibold tracking-tight">Transactions</h1>
        <CreateTransactionDialog />
      </header>
      <section aria-label="All transactions" className="overflow-hidden rounded-xl border bg-card shadow-xs">
        <TransactionsList />
      </section>
    </div>
  )
}

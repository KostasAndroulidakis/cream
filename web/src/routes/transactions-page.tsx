import { PageHeader } from "@/components/page-header"
import { CreateTransactionDialog } from "@/features/transactions/components/create-transaction-dialog"
import { TransactionsCard } from "@/features/transactions/components/transactions-card"

export function TransactionsPage() {
  return (
    <div className="space-y-4">
      <PageHeader title="Transactions" actions={<CreateTransactionDialog />} />
      <section aria-label="Transactions list" className="overflow-hidden rounded-xl border bg-card shadow-xs">
        <TransactionsCard />
      </section>
    </div>
  )
}

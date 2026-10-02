import { PageColumns } from "@/components/page-columns"
import { Panel } from "@/components/panel"
import { InboxCountBadge } from "@/features/categorization/components/inbox-count-badge"
import { MerchantRules } from "@/features/categorization/components/merchant-rules"
import { ReviewInbox } from "@/features/categorization/components/review-inbox"

export function ReviewPage() {
  return (
    <div className="space-y-8">
      <header className="max-w-xl space-y-1">
        <h1 className="text-3xl font-semibold tracking-tight">Review</h1>
        <p className="text-muted-foreground">
          Most imports find their category on their own. The rest wait here: pick one, and CREAM can remember the
          merchant for next time.
        </p>
      </header>

      <PageColumns>
        <Panel id="inbox-heading" title="Uncategorized" action={<InboxCountBadge className="text-xs" />}>
          <ReviewInbox />
        </Panel>
        <Panel id="rules-heading" title="Merchant rules">
          <MerchantRules />
        </Panel>
      </PageColumns>
    </div>
  )
}

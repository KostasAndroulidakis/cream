import { PageColumns } from "@/components/page-columns"
import { PageHeader } from "@/components/page-header"
import { Panel } from "@/components/panel"
import { InboxCountBadge } from "@/features/categorization/components/inbox-count-badge"
import { MerchantRules } from "@/features/categorization/components/merchant-rules"
import { ReviewInbox } from "@/features/categorization/components/review-inbox"

export function ReviewPage() {
  return (
    <div className="space-y-8">
      <PageHeader title="Review" />

      <PageColumns>
        <Panel id="inbox-heading" title="Needs review" action={<InboxCountBadge className="text-xs" />}>
          <ReviewInbox />
        </Panel>
        <Panel id="rules-heading" title="Merchant rules">
          <MerchantRules />
        </Panel>
      </PageColumns>
    </div>
  )
}

import { pluralize } from "@/lib/text"
import type { CategorizeResult } from "./api"

/** What happened after categorizing, in one sentence for a status line. */
export function describeResult(result: CategorizeResult, categoryName: string): string {
  const parts = [`Moved to ${categoryName}`]
  if (result.similar_updated > 0) {
    parts.push(`with ${pluralize(result.similar_updated, "similar transaction")}`)
  }
  const sentence = `${parts.join(" ")}.`
  return result.rule ? `${sentence} Future ${result.rule.merchant_name} imports will follow.` : sentence
}

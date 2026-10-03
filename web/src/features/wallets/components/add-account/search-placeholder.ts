/** "Search 42 institutions…", once the count is known. */
export function searchPlaceholder(count: number | undefined): string {
  return count ? `Search ${count.toLocaleString()} institutions…` : "Search institutions…"
}

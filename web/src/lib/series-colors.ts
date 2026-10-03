// The categorical slots defined in index.css (--series-1 … --series-6), light and dark
const SERIES_COUNT = 6

/** The color of the n-th series (0-based), cycling once the slots run out. */
export function seriesColor(index: number): string {
  return `var(--series-${(index % SERIES_COUNT) + 1})`
}

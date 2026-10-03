import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { formatLongDate, formatShortDay } from "@/lib/dates"
import { formatCompactMoney, formatMoney } from "@/lib/money"
import type { NetWorthHistory } from "../api"

type Series = NetWorthHistory["series"][number]
// Recharts plots numbers; the exact decimal string stays alongside for the tooltip
type ChartPoint = { date: string; value: number; balance: string }

const CHART_HEIGHT = 300
const Y_AXIS_WIDTH = 72
const GRADIENT_ID = "net-worth-fill"
const LINE_COLOR = "var(--color-chart-accent)"
const GRID_COLOR = "var(--color-border)"
const AXIS_TEXT = { fill: "var(--color-muted-foreground)", fontSize: 12 }

type NetWorthTooltipProps = {
  active?: boolean
  // Recharts' hovered entries; each carries the ChartPoint it was drawn from
  payload?: readonly { payload?: unknown }[]
  currency: string
}

function NetWorthTooltip({ active, payload, currency }: NetWorthTooltipProps) {
  const point = payload?.[0]?.payload as ChartPoint | undefined
  if (!active || !point) return null
  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-sm shadow-md">
      <p className="text-muted-foreground">{formatLongDate(point.date)}</p>
      <p className="font-semibold tabular-nums">{formatMoney(point.balance, currency)}</p>
    </div>
  )
}

/** Net worth over the chosen range: a 2px line over a light wash, with a crosshair and tooltip on hover. */
export function NetWorthChart({ series }: { series: Series }) {
  const points: ChartPoint[] = series.points.map(({ date, balance }) => ({ date, value: Number(balance), balance }))

  return (
    <div role="img" aria-label={`Net worth from ${formatLongDate(series.points[0].date)} to today`}>
      <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
        <AreaChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={GRADIENT_ID} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={LINE_COLOR} stopOpacity={0.18} />
              <stop offset="100%" stopColor={LINE_COLOR} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke={GRID_COLOR} />
          <XAxis
            dataKey="date"
            tickFormatter={formatShortDay}
            tick={AXIS_TEXT}
            tickLine={false}
            axisLine={false}
            minTickGap={32}
            tickMargin={10}
          />
          <YAxis
            tickFormatter={(value: number) => formatCompactMoney(value, series.currency)}
            tick={AXIS_TEXT}
            tickLine={false}
            axisLine={false}
            width={Y_AXIS_WIDTH}
            domain={["auto", "auto"]}
          />
          <Tooltip
            content={({ active, payload }) => (
              <NetWorthTooltip active={active} payload={payload} currency={series.currency} />
            )}
            cursor={{ stroke: GRID_COLOR, strokeWidth: 1 }}
          />
          <Area
            type="linear"
            dataKey="value"
            stroke={LINE_COLOR}
            strokeWidth={2}
            fill={`url(#${GRADIENT_ID})`}
            activeDot={{ r: 4, strokeWidth: 2, stroke: "var(--color-card)" }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

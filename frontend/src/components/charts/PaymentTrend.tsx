import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatMoney } from '@/lib/format'

interface Point {
  mes: string
  total: number
}

export function PaymentTrend({ data }: { data: Point[] }) {
  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
          <defs>
            <linearGradient id="payment-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.32} />
              <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="var(--line)" strokeDasharray="4 6" />
          <XAxis
            dataKey="mes"
            axisLine={false}
            tickLine={false}
            tick={{ fill: 'var(--ink-muted)', fontSize: 12 }}
            dy={8}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: 'var(--ink-muted)', fontSize: 11 }}
            tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}
          />
          <Tooltip
            cursor={{ stroke: 'var(--line-strong)', strokeDasharray: '4 4' }}
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              return (
                <div className="rounded-control border border-line bg-raised px-3 py-2 shadow-pop">
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-ink-muted">{label}</p>
                  <p className="tabular mt-1 text-sm font-bold text-ink">
                    {formatMoney(Number(payload[0]?.value ?? 0))}
                  </p>
                </div>
              )
            }}
          />
          <Area
            type="monotone"
            dataKey="total"
            stroke="var(--brand)"
            strokeWidth={2.5}
            fill="url(#payment-fill)"
            dot={{ r: 3, fill: 'var(--brand)', stroke: 'var(--surface)', strokeWidth: 2 }}
            activeDot={{ r: 5, fill: 'var(--brand)', stroke: 'var(--surface)', strokeWidth: 2 }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

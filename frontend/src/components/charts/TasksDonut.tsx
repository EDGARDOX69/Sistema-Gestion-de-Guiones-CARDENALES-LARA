import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

interface Point {
  estado: string
  value: number
}

const COLORS: Record<string, string> = {
  Pendiente: 'var(--time)',
  'En progreso': 'var(--info)',
  Completada: 'var(--live)',
}

export function TasksDonut({ data }: { data: Point[] }) {
  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <div>
      <div className="relative h-[210px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="estado"
              innerRadius={62}
              outerRadius={86}
              paddingAngle={4}
              stroke="none"
              isAnimationActive={false}
            >
              {data.map((entry) => (
                <Cell key={entry.estado} fill={COLORS[entry.estado] ?? 'var(--ink-faint)'} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const item = payload[0]
                return (
                  <div className="rounded-control border border-line bg-raised px-3 py-2 shadow-pop">
                    <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-ink-muted">
                      {item.name}
                    </p>
                    <p className="tabular mt-1 text-sm font-bold text-ink">{item.value} tareas</p>
                  </div>
                )
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="display text-3xl font-semibold text-ink">{total}</span>
          <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-muted">Tareas</span>
        </div>
      </div>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
        {data.map((item) => (
          <span key={item.estado} className="inline-flex items-center gap-1.5 text-[11px] text-ink-muted">
            <span className="size-1.5 rounded-full" style={{ background: COLORS[item.estado] }} />
            {item.estado}
            <span className="tabular font-semibold text-ink-soft">{item.value}</span>
          </span>
        ))}
      </div>
    </div>
  )
}

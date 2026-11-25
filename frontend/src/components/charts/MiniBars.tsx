import { cn } from '@/lib/cn'

interface Point {
  label: string
  value: number
}

export function MiniBars({
  data,
  color = 'var(--brand)',
  className,
  height = 'h-12',
}: {
  data: Point[]
  color?: string
  className?: string
  height?: string
}) {
  const max = Math.max(...data.map((item) => item.value), 1)
  return (
    <div className={cn('flex w-full items-end gap-1.5', className)}>
      {data.map((item) => (
        <div key={item.label} className="flex min-w-0 flex-1 flex-col items-center gap-1">
          <div className={cn('flex w-full items-end overflow-hidden rounded-sm bg-sunken/70', height)}>
            <div
              className="w-full rounded-sm opacity-90"
              style={{ height: `${Math.max(8, (item.value / max) * 100)}%`, backgroundColor: color }}
            />
          </div>
          <span className="text-[8px] font-semibold uppercase tracking-wide text-ink-faint">{item.label}</span>
        </div>
      ))}
    </div>
  )
}

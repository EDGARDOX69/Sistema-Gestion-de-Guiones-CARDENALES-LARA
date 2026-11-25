import type { LucideIcon } from 'lucide-react'
import type { Tone } from '@/components/ui/Badge'
import { cn } from '@/lib/cn'

interface Item {
  label: string
  value: string
  hint?: string
  tone?: Tone
  icon?: LucideIcon
}

const valueTones: Record<Tone, string> = {
  neutral: 'text-ink',
  brand: 'text-brand',
  live: 'text-live',
  time: 'text-time',
  info: 'text-info',
  danger: 'text-danger',
}

export function ScoreboardStrip({ items, className }: { items: Item[]; className?: string }) {
  return (
    <div
      className={cn(
        'grid grid-cols-2 gap-px overflow-hidden rounded-card border border-line bg-line lg:grid-cols-4',
        className,
      )}
    >
      {items.map((item) => {
        const Icon = item.icon
        return (
          <div key={item.label} className="bg-surface p-4 sm:p-5">
            <div className="flex items-center justify-between gap-2">
              <p className="eyebrow">{item.label}</p>
              {Icon && <Icon className="size-3.5 text-ink-faint" />}
            </div>
            <p className={cn('tabular display mt-2 text-2xl font-semibold sm:text-3xl', valueTones[item.tone ?? 'neutral'])}>
              {item.value}
            </p>
            {item.hint && <p className="mt-1 text-[11px] text-ink-muted">{item.hint}</p>}
          </div>
        )
      })}
    </div>
  )
}

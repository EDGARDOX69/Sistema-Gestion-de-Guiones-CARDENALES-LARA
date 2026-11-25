import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Option {
  value: string
  label: string
  icon?: LucideIcon
}

export function SegmentedControl({
  value,
  onValueChange,
  options,
  className,
  ariaLabel,
}: {
  value: string
  onValueChange: (value: string) => void
  options: Option[]
  className?: string
  ariaLabel?: string
}) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className={cn('inline-flex flex-wrap items-center gap-1 rounded-control border border-line bg-sunken/60 p-1', className)}
    >
      {options.map((option) => {
        const Icon = option.icon
        const active = option.value === value
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onValueChange(option.value)}
            aria-pressed={active}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors',
              active ? 'bg-surface text-ink shadow-card' : 'text-ink-muted hover:text-ink',
            )}
          >
            {Icon && <Icon className="size-3.5" />}
            {option.label}
          </button>
        )
      })}
    </div>
  )
}

import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

type Tone = 'brand' | 'live' | 'time' | 'info' | 'danger'

const fills: Record<Tone, string> = {
  brand: 'bg-brand',
  live: 'bg-live',
  time: 'bg-time',
  info: 'bg-info',
  danger: 'bg-danger',
}

export function Progress({
  value,
  tone = 'brand',
  size = 'md',
  label,
  className,
}: {
  value: number
  tone?: Tone
  size?: 'sm' | 'md'
  label?: string
  className?: string
}) {
  const safe = Math.min(100, Math.max(0, value))
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(safe)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
      className={cn('w-full overflow-hidden rounded-full bg-sunken', size === 'sm' ? 'h-1.5' : 'h-2', className)}
    >
      <div
        className={cn('h-full rounded-full transition-[width] duration-500', fills[tone])}
        style={{ width: `${safe}%` }}
      />
    </div>
  )
}

export function ProgressRing({
  value,
  size = 128,
  stroke = 9,
  color = 'var(--brand)',
  children,
  className,
}: {
  value: number
  size?: number
  stroke?: number
  color?: string
  children?: ReactNode
  className?: string
}) {
  const safe = Math.min(100, Math.max(0, value))
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (safe / 100) * circumference

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--line)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-[stroke-dashoffset] duration-500"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">{children}</div>
    </div>
  )
}

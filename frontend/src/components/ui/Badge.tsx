import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export type Tone = 'neutral' | 'brand' | 'live' | 'time' | 'info' | 'danger'

const tones: Record<Tone, string> = {
  neutral: 'border-line bg-sunken text-ink-soft',
  brand: 'border-brand/20 bg-brand-soft text-brand',
  live: 'border-live/20 bg-live-soft text-live',
  time: 'border-time/20 bg-time-soft text-time',
  info: 'border-info/20 bg-info-soft text-info',
  danger: 'border-danger/20 bg-danger-soft text-danger',
}

const dotTones: Record<Tone, string> = {
  neutral: 'bg-ink-faint',
  brand: 'bg-brand',
  live: 'bg-live',
  time: 'bg-time',
  info: 'bg-info',
  danger: 'bg-danger',
}

export function Badge({
  tone = 'neutral',
  size = 'md',
  dot = false,
  className,
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone; size?: 'sm' | 'md'; dot?: boolean }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border font-semibold',
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]',
        tones[tone],
        className,
      )}
      {...props}
    >
      {dot && <span className={cn('size-1.5 rounded-full', dotTones[tone])} />}
      {children}
    </span>
  )
}

export function StatusDot({
  tone = 'neutral',
  pulse = false,
  className,
}: {
  tone?: Tone
  pulse?: boolean
  className?: string
}) {
  return (
    <span className={cn('relative inline-flex size-2', className)}>
      {pulse && (
        <span className={cn('absolute inline-flex size-full rounded-full opacity-60', dotTones[tone], 'live-dot')} />
      )}
      <span className={cn('relative inline-flex size-2 rounded-full', dotTones[tone])} />
    </span>
  )
}

import { cn } from '@/lib/cn'
import { initials } from '@/lib/format'

type Size = 'xs' | 'sm' | 'md' | 'lg'

const sizes: Record<Size, string> = {
  xs: 'size-6 text-[9px]',
  sm: 'size-8 text-[10px]',
  md: 'size-10 text-xs',
  lg: 'size-14 text-base',
}

const tones = [
  'bg-brand-soft text-brand',
  'bg-live-soft text-live',
  'bg-info-soft text-info',
  'bg-time-soft text-time',
  'bg-sunken text-ink-soft',
]

export function Avatar({
  name,
  size = 'md',
  className,
}: {
  name: string
  size?: Size
  className?: string
}) {
  const tone = tones[name.charCodeAt(0) % tones.length]
  return (
    <span
      className={cn(
        'inline-grid shrink-0 place-items-center rounded-full border border-line font-bold uppercase tracking-wide',
        sizes[size],
        tone,
        className,
      )}
      title={name}
    >
      {initials(name)}
    </span>
  )
}

export function AvatarStack({ names, size = 'sm' }: { names: string[]; size?: Size }) {
  return (
    <div className="flex items-center">
      {names.map((name) => (
        <Avatar key={name} name={name} size={size} className="-ml-2 ring-2 ring-surface first:ml-0" />
      ))}
    </div>
  )
}

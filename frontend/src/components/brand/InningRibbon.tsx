import { cn } from '@/lib/cn'

export function InningRibbon({
  activeInning,
  completedInnings = [],
  className,
}: {
  activeInning?: number | null
  completedInnings?: number[]
  className?: string
}) {
  return (
    <div className={className}>
      <div className="mb-2 flex items-center justify-between">
        <p className="eyebrow">Innings</p>
        <p className="text-[10px] font-medium text-ink-faint">1 – 9</p>
      </div>
      <div className="grid grid-cols-9 gap-1" role="img" aria-label="Estado de los innings">
        {Array.from({ length: 9 }, (_, index) => {
          const inning = index + 1
          const completed = completedInnings.includes(inning)
          const active = activeInning === inning
          return (
            <div
              key={inning}
              className={cn(
                'grid h-7 place-items-center rounded-md border font-mono text-[10px] font-bold',
                completed && 'border-live/25 bg-live-soft text-live',
                active && 'border-time bg-time text-night-950',
                !completed && !active && 'border-line bg-sunken text-ink-faint',
              )}
            >
              {inning}
            </div>
          )
        })}
      </div>
    </div>
  )
}

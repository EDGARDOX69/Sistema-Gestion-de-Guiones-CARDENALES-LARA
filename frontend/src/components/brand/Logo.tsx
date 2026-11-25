import { cn } from '@/lib/cn'

export function Logo({
  size = 'md',
  withWordmark = true,
  tone = 'default',
  className,
}: {
  size?: 'sm' | 'md' | 'lg'
  withWordmark?: boolean
  tone?: 'default' | 'light'
  className?: string
}) {
  const tile =
    size === 'lg' ? 'size-14 rounded-card' : size === 'sm' ? 'size-9 rounded-control' : 'size-11 rounded-control'
  const image = size === 'lg' ? 'size-10' : size === 'sm' ? 'size-6' : 'size-8'

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <span
        className={cn(
          'grid shrink-0 place-items-center bg-night-950 ring-1 ring-white/10',
          tile,
        )}
      >
        <img src="/logo-blanco.png" alt="Itinerario" className={cn('object-contain', image)} />
      </span>
      {withWordmark && (
        <span className="min-w-0">
          <span
            className={cn(
              'display block text-lg font-semibold leading-none tracking-[0.08em]',
              tone === 'light' ? 'text-chalk' : 'text-ink',
            )}
          >
            ITINERARIO
          </span>
          <span
            className={cn(
              'mt-1 block text-[9px] font-bold uppercase leading-none tracking-[0.2em]',
              tone === 'light' ? 'text-chalk/55' : 'text-ink-muted',
            )}
          >
            Palco de Operaciones
          </span>
        </span>
      )}
    </div>
  )
}

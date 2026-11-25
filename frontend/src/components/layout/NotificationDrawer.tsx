import { BellOff, ClipboardCheck, Radio, ScrollText, Wallet } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Drawer } from '@/components/ui/Drawer'
import { EmptyState } from '@/components/ui/EmptyState'
import { useData } from '@/hooks/useData'
import { cn } from '@/lib/cn'

const ICONS = {
  tarea: ClipboardCheck,
  pago: Wallet,
  guion: ScrollText,
  sistema: Radio,
}

const TONES = {
  tarea: 'bg-time-soft text-time',
  pago: 'bg-live-soft text-live',
  guion: 'bg-info-soft text-info',
  sistema: 'bg-brand-soft text-brand',
}

export function NotificationDrawer({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { notificaciones, unreadCount, markRead, markAllRead } = useData()

  return (
    <Drawer
      open={open}
      onOpenChange={onOpenChange}
      title="Notificaciones"
      description={unreadCount > 0 ? `${unreadCount} sin leer` : 'Todo al día'}
      footer={
        <Button variant="secondary" onClick={markAllRead} disabled={unreadCount === 0}>
          Marcar todas como leídas
        </Button>
      }
    >
      {notificaciones.length === 0 ? (
        <EmptyState
          icon={BellOff}
          title="Sin notificaciones"
          description="Cuando haya movimientos en tus módulos aparecerán aquí."
        />
      ) : (
        <div className="space-y-1">
          {notificaciones.map((item) => {
            const Icon = ICONS[item.tipo]
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => markRead(item.id)}
                className={cn(
                  'flex w-full items-start gap-3 rounded-control p-3 text-left transition-colors hover:bg-sunken/70',
                  !item.leida && 'bg-brand-soft/25',
                )}
              >
                <span className={cn('grid size-9 shrink-0 place-items-center rounded-control', TONES[item.tipo])}>
                  <Icon className="size-4" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-2">
                    <span className="truncate text-sm font-semibold text-ink">{item.titulo}</span>
                    {!item.leida && <span className="size-1.5 shrink-0 rounded-full bg-brand" />}
                  </span>
                  <span className="mt-0.5 block text-xs leading-relaxed text-ink-muted">{item.mensaje}</span>
                  <span className="mt-1 block text-[10px] font-medium uppercase tracking-wide text-ink-faint">
                    {item.tiempo}
                  </span>
                </span>
              </button>
            )
          })}
        </div>
      )}
    </Drawer>
  )
}

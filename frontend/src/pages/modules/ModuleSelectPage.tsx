import { motion } from 'motion/react'
import { ArrowRight, ArrowUpRight, Check, Radio, UsersRound } from 'lucide-react'
import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { MiniBars } from '@/components/charts/MiniBars'
import { FieldLines } from '@/components/brand/FieldLines'
import { Logo } from '@/components/brand/Logo'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { UserMenu } from '@/components/layout/UserMenu'
import { Avatar, AvatarStack } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Progress, ProgressRing } from '@/components/ui/Progress'
import { SegmentBar } from '@/components/ui/SegmentBar'
import { useData } from '@/hooks/useData'
import { useLiveShow } from '@/hooks/useLiveShow'
import { useSession } from '@/hooks/useSession'
import { cn } from '@/lib/cn'
import {
  DEMO_DATE,
  MODULOS,
  MODULE_ACCENT,
} from '@/lib/constants'
import { daysUntil, formatDateLong, formatMoney, percent } from '@/lib/format'
import { pagosPorMes, recursosPorEstado, totalContratado, totalPagado } from '@/lib/selectors'
import type { ModuleId } from '@/types'

function ModuleCardShell({
  id,
  index,
  title,
  description,
  selected,
  onSelect,
  className,
  children,
}: {
  id: ModuleId
  index: number
  title: string
  description: string
  selected: boolean
  onSelect: () => void
  className?: string
  children: ReactNode
}) {
  const accent = MODULE_ACCENT[id]

  return (
    <motion.button
      type="button"
      onClick={onSelect}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.04 * index, duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.995 }}
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-card border bg-surface p-5 text-left shadow-card transition-[border-color,box-shadow] hover:border-line-strong hover:shadow-pop',
        selected ? 'border-brand ring-2 ring-brand/20' : 'border-line',
        className,
      )}
    >
      <span className={cn('pointer-events-none absolute inset-x-0 top-0 h-0.5 opacity-80', accent.dot)} />
      <span
        className={cn(
          'pointer-events-none absolute -right-16 -top-20 size-48 rounded-full opacity-0 blur-3xl transition-opacity duration-300 group-hover:opacity-30',
          accent.bg,
        )}
      />
      <span className="display pointer-events-none absolute -right-1 -top-6 text-7xl font-bold text-ink-faint/10">
        {String(index + 1).padStart(2, '0')}
      </span>
      <div className="relative flex items-start justify-between gap-3">
        <span className={cn('grid size-11 place-items-center rounded-control', accent.bg, accent.text)}>
          <ModuleIcon id={id} className="size-5" />
        </span>
        <span className="flex items-center gap-2">
          {selected && (
            <span className="inline-flex items-center gap-1 rounded-full bg-brand-soft px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-brand">
              <Check className="size-3" />
              Activo
            </span>
          )}
          <span className="grid size-8 place-items-center rounded-full border border-line bg-surface text-ink-muted transition-colors group-hover:border-brand/30 group-hover:text-brand">
            <ArrowUpRight className="size-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </span>
        </span>
      </div>
      <div className="relative mt-5">
        <h2 className="display text-2xl font-semibold text-ink">{title}</h2>
        <p className="mt-1 max-w-sm text-xs leading-relaxed text-ink-muted">{description}</p>
      </div>
      <div className="relative mt-auto pt-5">{children}</div>
    </motion.button>
  )
}

export function ModuleSelectPage() {
  const navigate = useNavigate()
  const { user, selectedModule, setModule } = useSession()
  const { patrocinadores, contratos, pagos, recursos, tareas, guiones } = useData()
  const live = useLiveShow()

  const contratado = totalContratado(contratos)
  const pagado = totalPagado(pagos)
  const saldo = Math.max(0, contratado - pagado)
  const activos = contratos.filter((contrato) => contrato.estado === 'Vigente').length
  const porVencer = contratos.filter((contrato) => {
    const dias = daysUntil(contrato.fin)
    return dias >= 0 && dias <= 45
  }).length
  const inventario = recursosPorEstado(recursos)
  const tareasCompletadas = tareas.filter((tarea) => tarea.estado === 'Completada').length
  const tareasPendientes = tareas.filter((tarea) => tarea.estado === 'Pendiente').length
  const tareasEnProgreso = tareas.filter((tarea) => tarea.estado === 'En progreso').length
  const tareasPct = percent(tareasCompletadas, tareas.length)
  const pagosMes = pagosPorMes(pagos)
  const guionVivo = guiones.find((guion) => guion.id === live.activeGuionId) ?? guiones[0]

  const seleccionar = (id: ModuleId) => {
    setModule(id)
    navigate('/app/dashboard')
  }

  return (
    <div className="relative min-h-dvh overflow-hidden bg-canvas">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[28rem] aurora opacity-40" />
      <FieldLines className="pointer-events-none absolute -right-40 -top-40 size-[560px] text-brand/[0.04]" />
      <header className="relative z-10 flex items-center justify-between gap-4 px-4 py-5 sm:px-6 lg:px-10">
        <Logo />
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <UserMenu />
        </div>
      </header>

      <main className="relative z-10 mx-auto w-full max-w-[1400px] px-4 pb-16 pt-4 sm:px-6 lg:px-10 lg:pt-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <p className="eyebrow">Jornada de operaciones</p>
            <h1 className="display mt-2 text-4xl font-semibold text-ink sm:text-5xl">
              Elige tu puesto en el palco.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-ink-muted">
              Tu sesión quedará enfocada en un solo módulo. Puedes cambiarlo cuando la jornada lo requiera.
            </p>
          </div>
          <div className="flex flex-col items-start gap-2 lg:items-end">
            <span className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-ink-muted">
              <UsersRound className="size-3.5" />
              {formatDateLong(DEMO_DATE)}
            </span>
            {user && (
              <span className="text-[11px] text-ink-muted">
                Sesión de <strong className="text-ink">{user.nombre}</strong> · {user.rol}
              </span>
            )}
          </div>
        </div>

        {selectedModule && (
          <Card className="mt-6 flex flex-col gap-4 border-brand/25 bg-brand-soft/35 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <span className="grid size-10 place-items-center rounded-control bg-surface text-brand">
                <ModuleIcon id={selectedModule as ModuleId} className="size-5" />
              </span>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-brand">Módulo seleccionado</p>
                <p className="text-sm font-bold text-ink">
                  {MODULOS.find((modulo) => modulo.id === selectedModule)?.nombre}
                </p>
              </div>
            </div>
            <Button onClick={() => navigate('/app/dashboard')} rightIcon={<ArrowRight className="size-4" />}>
              Continuar jornada
            </Button>
          </Card>
        )}

        <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-12">
          <ModuleCardShell
            id="patrocinantes"
            index={0}
            title="Patrocinantes"
            description="Marcas, contratos y contacto comercial de la temporada."
            selected={selectedModule === 'patrocinantes'}
            onSelect={() => seleccionar('patrocinantes')}
            className="lg:col-span-7"
          >
            <div className="mb-4 grid grid-cols-3 gap-2 border-y border-line/70 py-3 text-center">
              <div>
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-ink-faint">Vigentes</p>
                <p className="display tabular mt-0.5 text-base font-semibold text-ink">{activos}</p>
              </div>
              <div>
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-ink-faint">Por vencer</p>
                <p className="display tabular mt-0.5 text-base font-semibold text-time">{porVencer}</p>
              </div>
              <div>
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-ink-faint">Marcas</p>
                <p className="display tabular mt-0.5 text-base font-semibold text-brand">{patrocinadores.length}</p>
              </div>
            </div>
            <div className="flex items-center justify-between gap-4">
              <div>
                <AvatarStack names={patrocinadores.slice(0, 4).map((item) => item.nombre)} size="sm" />
                <p className="mt-2 text-[11px] text-ink-muted">
                  {patrocinadores.length} marcas activas · {activos} contratos vigentes
                </p>
              </div>
              <div className="text-right">
                <p className="display tabular text-2xl font-semibold text-brand">{formatMoney(contratado)}</p>
                <p className="text-[10px] uppercase tracking-[0.12em] text-ink-faint">Contratado</p>
              </div>
            </div>
          </ModuleCardShell>

          <ModuleCardShell
            id="balance"
            index={1}
            title="Balance"
            description="Cobranza, pagos y estado de cuenta de cada contrato."
            selected={selectedModule === 'balance'}
            onSelect={() => seleccionar('balance')}
            className="lg:col-span-5"
          >
            <MiniBars
              data={pagosMes.map((item) => ({ label: item.mes, value: item.total }))}
              color="var(--live)"
              height="h-10"
              className="mb-4"
            />
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="display tabular text-3xl font-semibold text-live">{formatMoney(saldo)}</p>
                <p className="text-[10px] uppercase tracking-[0.12em] text-ink-faint">Saldo por cobrar</p>
              </div>
              <Badge tone="live" dot>
                {activos} activos
              </Badge>
            </div>
            <div className="mt-4">
              <Progress value={percent(pagado, contratado)} tone="live" size="sm" label="Avance de cobranza" />
              <div className="mt-2 flex items-center justify-between text-[10px] text-ink-muted">
                <span>{formatMoney(pagado)} pagados</span>
                <span>{Math.round(percent(pagado, contratado))}%</span>
              </div>
            </div>
          </ModuleCardShell>

          <ModuleCardShell
            id="inventario"
            index={2}
            title="Inventario"
            description="Recursos, tipos y asignaciones del equipo."
            selected={selectedModule === 'inventario'}
            onSelect={() => seleccionar('inventario')}
            className="lg:col-span-4"
          >
            <div className="space-y-2 text-[11px]">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-ink-muted">
                  <span className="size-1.5 rounded-full bg-live" /> Disponibles
                </span>
                <span className="tabular font-semibold text-ink">{inventario.disponibles}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-ink-muted">
                  <span className="size-1.5 rounded-full bg-info" /> Asignados
                </span>
                <span className="tabular font-semibold text-ink">{inventario.asignados}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-ink-muted">
                  <span className="size-1.5 rounded-full bg-time" /> Mantenimiento
                </span>
                <span className="tabular font-semibold text-ink">{inventario.mantenimiento}</span>
              </div>
            </div>
            <SegmentBar
              className="mt-3"
              segments={[
                { value: inventario.disponibles, className: 'bg-live' },
                { value: inventario.asignados, className: 'bg-info' },
                { value: inventario.mantenimiento, className: 'bg-time' },
              ]}
            />
            <div className="mt-3 flex items-center justify-between border-t border-line pt-3">
              <span className="text-[10px] uppercase tracking-[0.12em] text-ink-faint">Valor total</span>
              <span className="display tabular text-lg font-semibold text-info">{formatMoney(inventario.valor)}</span>
            </div>
          </ModuleCardShell>

          <ModuleCardShell
            id="tareas"
            index={3}
            title="Tareas"
            description="Asignaciones y avance de la jornada."
            selected={selectedModule === 'tareas'}
            onSelect={() => seleccionar('tareas')}
            className="lg:col-span-4"
          >
            <div className="flex items-center gap-4">
              <ProgressRing value={tareasPct} size={74} stroke={7} color="var(--time)">
                <span className="display tabular text-base font-semibold text-ink">{tareasPct}%</span>
              </ProgressRing>
              <div>
                <p className="text-sm font-bold text-ink">
                  {tareasCompletadas} de {tareas.length}
                </p>
                <p className="text-[11px] text-ink-muted">tareas completadas</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  <Badge tone="time" size="sm">{tareasPendientes} pendientes</Badge>
                  <Badge tone="info" size="sm">{tareasEnProgreso} en curso</Badge>
                </div>
              </div>
            </div>
            <SegmentBar
              className="mt-4"
              segments={[
                { value: tareasPendientes, className: 'bg-time' },
                { value: tareasEnProgreso, className: 'bg-info' },
                { value: tareasCompletadas, className: 'bg-live' },
              ]}
            />
          </ModuleCardShell>

          <ModuleCardShell
            id="guion"
            index={4}
            title="Guion"
            description="Guiones del juego y control del show en vivo."
            selected={selectedModule === 'guion'}
            onSelect={() => seleccionar('guion')}
            className="lg:col-span-4"
          >
            <div className="rounded-control border border-live/20 bg-live-soft p-3">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-[0.14em] text-live">
                  <Radio className="size-3" />
                  {live.status === 'live' ? 'En vivo' : 'Sin show'}
                </span>
                <span className="tabular text-[10px] font-semibold text-live">{live.progress}%</span>
              </div>
              <p className="mt-1.5 truncate text-xs font-semibold text-ink">
                {live.status === 'live'
                  ? live.currentElement?.contenido ?? 'Show listo para iniciar'
                  : 'Cardenales vs Leones'}
              </p>
              <div className="mt-2 flex items-center justify-between text-[10px] text-ink-muted">
                <span>{guionVivo?.elementos.length ?? 0} elementos</span>
                <span>{guiones.length} guiones</span>
              </div>
            </div>
          </ModuleCardShell>
        </div>

        <div className="mt-8 flex flex-col items-start justify-between gap-3 border-t border-line pt-5 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2.5">
            {user && <Avatar name={user.nombre} size="sm" />}
            <p className="text-[11px] text-ink-muted">
              Sesión de <strong className="text-ink">{user?.nombre}</strong> · {user?.departamento}
            </p>
          </div>
          <p className="text-[10px] uppercase tracking-[0.14em] text-ink-faint">
            Estadio Antonio Herrera Gutiérrez · Barquisimeto
          </p>
        </div>
      </main>
    </div>
  )
}

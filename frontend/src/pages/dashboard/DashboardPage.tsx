import {
  ArrowLeftRight,
  ArrowRight,
  Boxes,
  ClipboardCheck,
  Handshake,
  Radio,
  RefreshCw,
  ScrollText,
  Wallet,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { FieldLines } from '@/components/brand/FieldLines'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { MiniBars } from '@/components/charts/MiniBars'
import { PaymentTrend } from '@/components/charts/PaymentTrend'
import { TasksDonut } from '@/components/charts/TasksDonut'
import { Avatar, AvatarStack } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PageHeader } from '@/components/ui/PageHeader'
import { Progress, ProgressRing } from '@/components/ui/Progress'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SegmentBar } from '@/components/ui/SegmentBar'
import { useData } from '@/hooks/useData'
import { useLiveClock } from '@/hooks/useLiveClock'
import { useLiveShow } from '@/hooks/useLiveShow'
import { useSession } from '@/hooks/useSession'
import { cn } from '@/lib/cn'
import { DEMO_DATE, MODULO_POR_ID, MODULE_ACCENT } from '@/lib/constants'
import {
  daysUntil,
  formatDate,
  formatDateLong,
  formatElapsed,
  formatMoney,
  nombreCorto,
  percent,
} from '@/lib/format'
import {
  pagosPorMes,
  recursosPorEstado,
  saldoContrato,
  tareasPorEstado,
  totalContratado,
  totalPagado,
} from '@/lib/selectors'
import type { ModuleId } from '@/types'
import type { Tone } from '@/components/ui/Badge'

function saludoActual() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Buenos días'
  if (hour < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

const ACTIVIDAD_ICONS = {
  pago: Wallet,
  guion: ScrollText,
  tarea: ClipboardCheck,
  patrocinador: Handshake,
  inventario: Boxes,
  sistema: Radio,
}

const ACTIVIDAD_TONES: Record<string, string> = {
  pago: 'bg-live-soft text-live',
  guion: 'bg-info-soft text-info',
  tarea: 'bg-time-soft text-time',
  patrocinador: 'bg-brand-soft text-brand',
  inventario: 'bg-info-soft text-info',
  sistema: 'bg-brand-soft text-brand',
}

function MiniStat({ label, value, tone = 'text-ink' }: { label: string; value: string; tone?: string }) {
  return (
    <div>
      <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-ink-faint">{label}</p>
      <p className={`display tabular mt-0.5 text-lg font-semibold ${tone}`}>{value}</p>
    </div>
  )
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-line py-2.5 last:border-0 last:pb-0 first:pt-0">
      <span className="text-xs text-ink-muted">{label}</span>
      <span className="tabular text-sm font-bold text-ink">{value}</span>
    </div>
  )
}

function HeroAction({
  to,
  children,
  variant = 'primary',
}: {
  to: string
  children: ReactNode
  variant?: 'primary' | 'secondary'
}) {
  return (
    <Button asChild variant={variant} size="sm">
      <Link to={to}>
        {children}
        <ArrowRight className="size-3.5" />
      </Link>
    </Button>
  )
}

export function DashboardPage() {
  const navigate = useNavigate()
  const { user, selectedModule, clearModule } = useSession()
  const {
    patrocinadores,
    contratos,
    pagos,
    recursos,
    tareas,
    guiones,
    asignaciones,
    usuarios,
    actividad,
  } = useData()
  const live = useLiveShow()
  const elapsed = useLiveClock(live.startedAt, live.status === 'live')

  const moduleId: ModuleId = selectedModule ?? 'guion'
  const moduleInfo = MODULO_POR_ID[moduleId]
  const accent = MODULE_ACCENT[moduleId]

  const contratado = totalContratado(contratos)
  const pagado = totalPagado(pagos)
  const saldo = Math.max(0, contratado - pagado)
  const activos = contratos.filter((contrato) => contrato.estado === 'Vigente').length
  const inventario = recursosPorEstado(recursos)
  const tareasCompletadas = tareas.filter((tarea) => tarea.estado === 'Completada').length
  const tareasPendientes = tareas.filter((tarea) => tarea.estado === 'Pendiente').length
  const tareasEnProgreso = tareas.filter((tarea) => tarea.estado === 'En progreso').length
  const tareasPct = percent(tareasCompletadas, tareas.length)
  const guionActual = guiones.find((guion) => guion.id === live.activeGuionId) ?? guiones[0]
  const porVencer = contratos.filter((contrato) => {
    const days = daysUntil(contrato.fin)
    return days >= 0 && days <= 45
  })
  const pagosMes = pagosPorMes(pagos)
  const tareasData = tareasPorEstado(tareas)

  const resumen = (() => {
    if (moduleId === 'patrocinantes') {
      return [
        { label: 'Marcas activas', value: String(patrocinadores.length) },
        { label: 'Contratos vigentes', value: String(activos) },
        { label: 'Por vencer', value: String(porVencer.length) },
      ]
    }
    if (moduleId === 'balance') {
      return [
        { label: 'Pagado', value: formatMoney(pagado) },
        { label: 'Pendiente', value: formatMoney(saldo) },
        { label: 'Pagos registrados', value: String(pagos.length) },
      ]
    }
    if (moduleId === 'inventario') {
      return [
        { label: 'Disponibles', value: String(inventario.disponibles) },
        { label: 'Asignados', value: String(inventario.asignados) },
        { label: 'Mantenimiento', value: String(inventario.mantenimiento) },
      ]
    }
    if (moduleId === 'tareas') {
      return [
        { label: 'Pendientes', value: String(tareas.filter((tarea) => tarea.estado === 'Pendiente').length) },
        { label: 'En progreso', value: String(tareas.filter((tarea) => tarea.estado === 'En progreso').length) },
        { label: 'Completadas', value: String(tareasCompletadas) },
      ]
    }
    return [
      { label: 'Guiones', value: String(guiones.length) },
      { label: 'Elementos', value: String(guionActual?.elementos.length ?? 0) },
      { label: 'Avance del show', value: `${live.progress}%` },
    ]
  })()

  const proximos: { title: string; meta: string; tone: Tone }[] = (() => {
    if (moduleId === 'guion') {
      return live.nextElements.slice(0, 4).map((elemento) => ({
        title: elemento.contenido,
        meta:
          elemento.tipo === 'Juego'
            ? `Inning ${elemento.inning} · ${elemento.medioInning}`
            : `${elemento.tipo} · ${elemento.hora ?? ''}`,
        tone: 'info',
      }))
    }
    if (moduleId === 'balance') {
      return contratos
        .filter((contrato) => saldoContrato(contrato, pagos) > 0)
        .slice(0, 4)
        .map((contrato) => {
          const patrocinador = patrocinadores.find((item) => item.id === contrato.patrocinadorId)
          return {
            title: patrocinador?.nombre ?? `Contrato #${contrato.id}`,
            meta: `${formatMoney(saldoContrato(contrato, pagos))} · vence ${formatDate(contrato.fin)}`,
            tone: 'live',
          }
        })
    }
    if (moduleId === 'patrocinantes') {
      return [...contratos]
        .sort((a, b) => daysUntil(a.fin) - daysUntil(b.fin))
        .slice(0, 4)
        .map((contrato) => {
          const patrocinador = patrocinadores.find((item) => item.id === contrato.patrocinadorId)
          return {
            title: patrocinador?.nombre ?? `Contrato #${contrato.id}`,
            meta: `Vence ${formatDate(contrato.fin)} · ${contrato.estado}`,
            tone: 'brand',
          }
        })
    }
    if (moduleId === 'inventario') {
      return asignaciones
        .filter((asignacion) => asignacion.estado === 'Pendiente')
        .slice(0, 4)
        .map((asignacion) => {
          const recurso = recursos.find((item) => item.id === asignacion.recursoId)
          const usuario = usuarios.find((item) => item.id === asignacion.usuarioId)
          return {
            title: recurso?.nombre ?? `Recurso #${asignacion.recursoId}`,
            meta: `${usuario?.nombre ?? 'Sin usuario'} · devolución ${formatDate(asignacion.fechaDevolucionEsperada)}`,
            tone: 'info',
          }
        })
    }
    return tareas
      .filter((tarea) => tarea.estado !== 'Completada')
      .slice(0, 4)
      .map((tarea) => {
        const usuario = usuarios.find((item) => item.id === tarea.asignadoId)
        return {
          title: tarea.nombre,
          meta: `${usuario?.nombre ?? 'Sin asignar'} · ${formatDate(tarea.fecha)}`,
          tone: 'time',
        }
      })
  })()

  const cambiarModulo = () => {
    clearModule()
    navigate('/modulos')
  }

  const actualizar = () => {
    toast.success('Datos de la jornada al día')
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={formatDateLong(DEMO_DATE)}
        title={`${saludoActual()}, ${user?.nombre.split(' ')[0] ?? 'operador'}`}
        description={`Tu módulo: ${moduleInfo.nombre}. La jornada está en marcha.`}
        actions={
          <>
            <Button variant="secondary" size="sm" onClick={cambiarModulo} leftIcon={<ArrowLeftRight className="size-3.5" />}>
              Cambiar módulo
            </Button>
            <Button variant="ghost" size="icon" onClick={actualizar} aria-label="Actualizar datos">
              <RefreshCw className="size-4" />
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          {
            label: 'Patrocinantes',
            value: String(patrocinadores.length),
            hint: `${activos} contratos vigentes`,
            tone: 'brand',
            icon: Handshake,
          },
          {
            label: 'Balance pagado',
            value: formatMoney(pagado),
            hint: `${Math.round(percent(pagado, contratado))}% de ${formatMoney(contratado)}`,
            tone: 'live',
            icon: Wallet,
          },
          {
            label: 'Recursos',
            value: String(inventario.total),
            hint: `${inventario.disponibles} disponibles · ${inventario.asignados} asignados`,
            tone: 'info',
            icon: Boxes,
          },
          {
            label: 'Tareas',
            value: String(tareas.length),
            hint: `${tareasCompletadas} completadas`,
            tone: 'time',
            icon: ClipboardCheck,
          },
        ]}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <Card className="relative flex overflow-hidden p-5 sm:p-6 lg:col-span-8">
          <div className={cn('pointer-events-none absolute inset-0 opacity-70', accent.bg)} />
          <FieldLines className="pointer-events-none absolute -bottom-28 -right-24 size-[360px] text-ink/[0.05]" />
          <div className="relative flex h-full w-full flex-col justify-between">
            {moduleId === 'guion' && (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  {live.status === 'live' ? (
                    <Badge tone="live" dot>
                      En vivo
                    </Badge>
                  ) : (
                    <Badge tone="neutral">Sin show activo</Badge>
                  )}
                  <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-muted">
                    {guionActual ? nombreCorto(guionActual.nombre) : 'Guion de la jornada'}
                  </span>
                </div>
                <h2 className="display mt-4 max-w-xl text-3xl font-semibold text-ink sm:text-4xl">
                  {live.currentElement?.contenido ?? 'El show está listo para comenzar'}
                </h2>
                <p className="mt-2 text-xs text-ink-muted">
                  {live.currentElement
                    ? `${live.currentElement.tipo}${live.currentElement.inning ? ` · Inning ${live.currentElement.inning} ${live.currentElement.medioInning ?? ''}` : ''} · ${live.currentElement.encargado}`
                    : 'Abre el control para iniciar la secuencia de elementos.'}
                </p>
                <div className="mt-5 flex flex-wrap items-end gap-6">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-ink-faint">Tiempo de show</p>
                    <p className="tabular font-mono text-3xl font-bold text-ink">{formatElapsed(elapsed)}</p>
                  </div>
                  <div className="min-w-40 flex-1">
                    <div className="mb-1.5 flex items-center justify-between text-[10px] text-ink-muted">
                      <span>{live.completedCount} de {live.elements.length} completados</span>
                      <span>{live.progress}%</span>
                    </div>
                    <Progress value={live.progress} tone="live" />
                  </div>
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  <HeroAction to={live.status === 'live' ? `/app/guion/${live.activeGuionId ?? 1}/en-vivo` : '/app/guion'}>
                    {live.status === 'live' ? 'Abrir control' : 'Abrir guiones'}
                  </HeroAction>
                  <HeroAction to="/app/guion" variant="secondary">
                    Ver guiones
                  </HeroAction>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-3 border-t border-line/70 pt-4">
                  <MiniStat label="Completados" value={String(live.completedCount)} tone="text-live" />
                  <MiniStat label="Pendientes" value={String(live.pendingCount)} tone="text-time" />
                  <MiniStat label="Operadores" value={String(usuarios.filter((item) => item.activo).length)} />
                </div>
              </>
            )}

            {moduleId === 'balance' && (
              <>
                <Badge tone="live" dot>
                  Cobranza de la temporada
                </Badge>
                <h2 className="display mt-4 text-4xl font-semibold text-ink sm:text-5xl">{formatMoney(saldo)}</h2>
                <p className="mt-1 text-xs text-ink-muted">Saldo pendiente de {formatMoney(contratado)} contratados</p>
                <div className="mt-5 max-w-md">
                  <div className="mb-1.5 flex items-center justify-between text-[10px] text-ink-muted">
                    <span>{formatMoney(pagado)} pagados</span>
                    <span>{Math.round(percent(pagado, contratado))}%</span>
                  </div>
                  <Progress value={percent(pagado, contratado)} tone="live" />
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  <HeroAction to="/app/balance?pago=1">Registrar pago</HeroAction>
                  <HeroAction to="/app/balance" variant="secondary">
                    Ver balance
                  </HeroAction>
                </div>
                <div className="mt-6 border-t border-line/70 pt-4">
                  <div className="flex items-center justify-between">
                    <p className="eyebrow">Ritmo de cobranza</p>
                    <span className="text-[10px] text-ink-muted">Últimos 4 meses</span>
                  </div>
                  <MiniBars
                    data={pagosMes.map((item) => ({ label: item.mes, value: item.total }))}
                    color="var(--live)"
                    height="h-10"
                    className="mt-3"
                  />
                </div>
              </>
            )}

            {moduleId === 'patrocinantes' && (
              <>
                <Badge tone="brand" dot>
                  Cobertura comercial
                </Badge>
                <h2 className="display mt-4 text-4xl font-semibold text-ink sm:text-5xl">
                  {patrocinadores.length} marcas
                </h2>
                <p className="mt-1 text-xs text-ink-muted">
                  {activos} contratos vigentes · {porVencer.length} por vencer en los próximos 45 días
                </p>
                <div className="mt-5 flex items-center gap-3">
                  <AvatarStack names={patrocinadores.slice(0, 6).map((item) => item.nombre)} size="md" />
                  <span className="text-[11px] text-ink-muted">Marcas activas de la temporada</span>
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  <HeroAction to="/app/patrocinantes">Ver patrocinantes</HeroAction>
                  <HeroAction to="/app/patrocinantes?nuevo=1" variant="secondary">
                    Nuevo patrocinante
                  </HeroAction>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-3 border-t border-line/70 pt-4">
                  <MiniStat label="Vigentes" value={String(activos)} tone="text-live" />
                  <MiniStat label="Por vencer" value={String(porVencer.length)} tone="text-time" />
                  <MiniStat label="Cartera" value={formatMoney(contratado)} tone="text-brand" />
                </div>
              </>
            )}

            {moduleId === 'inventario' && (
              <>
                <Badge tone="info" dot>
                  Inventario operativo
                </Badge>
                <h2 className="display mt-4 text-4xl font-semibold text-ink sm:text-5xl">
                  {inventario.disponibles} disponibles
                </h2>
                <p className="mt-1 text-xs text-ink-muted">
                  {inventario.total} recursos · {formatMoney(inventario.valor)} en equipos
                </p>
                <div className="mt-5 max-w-md space-y-2">
                  {[
                    { label: 'Asignados', value: inventario.asignados, tone: 'info' as Tone },
                    { label: 'En mantenimiento', value: inventario.mantenimiento, tone: 'time' as Tone },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between rounded-control border border-line bg-surface/70 px-3 py-2">
                      <span className="text-xs text-ink-muted">{item.label}</span>
                      <Badge tone={item.tone} size="sm">
                        {item.value}
                      </Badge>
                    </div>
                  ))}
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  <HeroAction to="/app/inventario">Ver inventario</HeroAction>
                </div>
                <SegmentBar
                  className="mt-5"
                  segments={[
                    { value: inventario.disponibles, className: 'bg-live' },
                    { value: inventario.asignados, className: 'bg-info' },
                    { value: inventario.mantenimiento, className: 'bg-time' },
                  ]}
                />
                <div className="mt-4 grid grid-cols-3 gap-3 border-t border-line/70 pt-4">
                  <MiniStat label="Disponibles" value={String(inventario.disponibles)} tone="text-live" />
                  <MiniStat label="Asignados" value={String(inventario.asignados)} tone="text-info" />
                  <MiniStat label="Valor" value={formatMoney(inventario.valor)} tone="text-ink" />
                </div>
              </>
            )}

            {moduleId === 'tareas' && (
              <>
                <Badge tone="time" dot>
                  Jornada de tareas
                </Badge>
                <div className="mt-4 flex flex-wrap items-center gap-6">
                  <div>
                    <h2 className="display text-4xl font-semibold text-ink sm:text-5xl">{tareasPct}%</h2>
                    <p className="mt-1 text-xs text-ink-muted">
                      {tareasCompletadas} de {tareas.length} tareas completadas
                    </p>
                  </div>
                  <ProgressRing value={tareasPct} size={92} stroke={8} color="var(--time)">
                    <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-ink-muted">Avance</span>
                  </ProgressRing>
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  <HeroAction to="/app/tareas">Ver tablero</HeroAction>
                  <HeroAction to="/app/tareas?nueva=1" variant="secondary">
                    Nueva tarea
                  </HeroAction>
                </div>
                <SegmentBar
                  className="mt-5"
                  segments={[
                    { value: tareasPendientes, className: 'bg-time' },
                    { value: tareasEnProgreso, className: 'bg-info' },
                    { value: tareasCompletadas, className: 'bg-live' },
                  ]}
                />
                <div className="mt-4 grid grid-cols-3 gap-3 border-t border-line/70 pt-4">
                  <MiniStat label="Pendientes" value={String(tareasPendientes)} tone="text-time" />
                  <MiniStat label="En progreso" value={String(tareasEnProgreso)} tone="text-info" />
                  <MiniStat label="Completadas" value={String(tareasCompletadas)} tone="text-live" />
                </div>
              </>
            )}
          </div>
        </Card>

        <div className="space-y-4 lg:col-span-4">
          <Card className="p-5">
            <div className="flex items-center gap-2.5">
              <span className={cn('grid size-9 place-items-center rounded-control', accent.bg, accent.text)}>
                <ModuleIcon id={moduleId} className="size-4" />
              </span>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-ink-faint">Tu módulo</p>
                <p className="text-sm font-bold text-ink">{moduleInfo.nombre}</p>
              </div>
            </div>
            <div className="mt-4">
              {resumen.map((item) => (
                <StatRow key={item.label} label={item.label} value={item.value} />
              ))}
            </div>
            <Button asChild variant="secondary" className="mt-4 w-full">
              <Link to={moduleInfo.ruta}>
                Ir a {moduleInfo.nombre}
                <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </Card>

          <Card className="p-5">
            <div className="flex items-center justify-between">
              <p className="eyebrow">Equipo en línea</p>
              <Badge tone="live" dot>
                {usuarios.filter((item) => item.activo).length}
              </Badge>
            </div>
            <div className="mt-3 space-y-2.5">
              {usuarios
                .filter((item) => item.activo)
                .slice(0, 4)
                .map((usuario) => (
                  <div key={usuario.id} className="flex items-center gap-2.5">
                    <Avatar name={usuario.nombre} size="sm" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">{usuario.nombre}</p>
                      <p className="truncate text-[10px] text-ink-muted">{usuario.departamento}</p>
                    </div>
                    <span className="size-1.5 rounded-full bg-live" />
                  </div>
                ))}
            </div>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <Card className="p-5 lg:col-span-7">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="eyebrow">Ritmo de pagos</p>
              <p className="mt-1 text-sm font-bold text-ink">Abonos registrados por mes</p>
            </div>
            <Badge tone="live">{formatMoney(pagado)}</Badge>
          </div>
          <div className="mt-3">
            <PaymentTrend data={pagosMes} />
          </div>
        </Card>

        <Card className="p-5 lg:col-span-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="eyebrow">Tareas por estado</p>
              <p className="mt-1 text-sm font-bold text-ink">Distribución de la jornada</p>
            </div>
            <Badge tone="time">{tareas.length} total</Badge>
          </div>
          <TasksDonut data={tareasData} />
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <Card className="p-5 lg:col-span-7">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow">Actividad reciente</p>
              <p className="mt-1 text-sm font-bold text-ink">Últimos movimientos del palco</p>
            </div>
            <ScrollText className="size-4 text-ink-faint" />
          </div>
          <div className="mt-4 space-y-3">
            {actividad.slice(0, 5).map((item) => {
              const Icon = ACTIVIDAD_ICONS[item.tipo as keyof typeof ACTIVIDAD_ICONS] ?? Radio
              return (
                <div key={item.id} className="flex items-start gap-3">
                  <span className={cn('grid size-8 shrink-0 place-items-center rounded-control', ACTIVIDAD_TONES[item.tipo] ?? 'bg-sunken text-ink-muted')}>
                    <Icon className="size-3.5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-ink">{item.titulo}</p>
                    <p className="truncate text-[11px] text-ink-muted">{item.detalle}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] font-medium text-ink-faint">{item.tiempo}</p>
                    <p className="text-[10px] text-ink-muted">{item.usuario}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>

        <Card className="p-5 lg:col-span-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow">Próximos</p>
              <p className="mt-1 text-sm font-bold text-ink">En la jornada</p>
            </div>
            <ArrowRight className="size-4 text-ink-faint" />
          </div>
          <div className="mt-4 space-y-2">
            {proximos.length === 0 ? (
              <p className="rounded-control border border-dashed border-line-strong px-3 py-6 text-center text-xs text-ink-muted">
                Sin pendientes para mostrar.
              </p>
            ) : (
              proximos.map((item, index) => (
                <div key={`${item.title}-${index}`} className="flex items-start gap-3 rounded-control border border-line bg-sunken/35 px-3 py-2.5">
                  <span className={cn(
                    'mt-0.5 grid size-6 shrink-0 place-items-center rounded-full text-[10px] font-bold',
                    item.tone === 'live' && 'bg-live-soft text-live',
                    item.tone === 'brand' && 'bg-brand-soft text-brand',
                    item.tone === 'time' && 'bg-time-soft text-time',
                    item.tone === 'info' && 'bg-info-soft text-info',
                    item.tone === 'danger' && 'bg-danger-soft text-danger',
                    item.tone === 'neutral' && 'bg-sunken text-ink-muted',
                  )}>
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-semibold text-ink">{item.title}</p>
                    <p className="truncate text-[10px] text-ink-muted">{item.meta}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

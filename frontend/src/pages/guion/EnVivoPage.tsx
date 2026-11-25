import {
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  LogOut,
  Radio,
  RotateCcw,
  Users,
  Wifi,
} from 'lucide-react'
import { useCallback, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { FieldLines } from '@/components/brand/FieldLines'
import { InningRibbon } from '@/components/brand/InningRibbon'
import { Logo } from '@/components/brand/Logo'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { ProgressRing } from '@/components/ui/Progress'
import { useData } from '@/hooks/useData'
import { useDoubleTap } from '@/hooks/useDoubleTap'
import { useLiveClock } from '@/hooks/useLiveClock'
import { useLiveShow } from '@/hooks/useLiveShow'
import type { FinishSummary } from '@/context/LiveProvider'
import { cn } from '@/lib/cn'
import { formatDuration, formatElapsed, formatTime, nombreCorto } from '@/lib/format'

interface LogEntry {
  id: number
  time: string
  text: string
}

function horaActual() {
  return new Date().toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })
}

export function EnVivoPage() {
  const navigate = useNavigate()
  const { guiones, usuarios, updateGuionEstado, notify } = useData()
  const live = useLiveShow()
  const elapsed = useLiveClock(live.startedAt, live.status === 'live')
  const [confirmFinish, setConfirmFinish] = useState(false)
  const [summary, setSummary] = useState<FinishSummary | null>(null)
  const [showName, setShowName] = useState('')
  const [log, setLog] = useState<LogEntry[]>([
    { id: 1, time: '17:00', text: 'Show iniciado y sincronizado con el palco.' },
  ])

  const guion = guiones.find((item) => item.id === live.activeGuionId)
  const publicado = guiones.find((item) => item.estado === 'Publicado')
  const current = live.currentElement
  const showLabel = guion ? nombreCorto(guion.nombre) : 'Show en vivo'

  const addLog = useCallback((text: string) => {
    setLog((prev) => [{ id: Date.now(), time: horaActual(), text }, ...prev].slice(0, 10))
  }, [])

  const avanzar = useCallback(() => {
    if (!live.currentElement) return
    addLog(`Avanzó: ${live.currentElement.contenido}`)
    live.advance()
  }, [addLog, live])

  const retroceder = useCallback(() => {
    if (!live.currentElement) return
    addLog(`Retrocedió: ${live.currentElement.contenido}`)
    live.back()
  }, [addLog, live])

  const handleTap = useDoubleTap(avanzar)

  const iniciarDesdeAqui = () => {
    if (!publicado) {
      toast.error('No hay un guion publicado para iniciar')
      return
    }
    live.start(publicado.id, publicado.elementos)
    updateGuionEstado(publicado.id, 'En vivo')
    addLog(`Show iniciado: ${publicado.nombre}`)
    toast.success('Show iniciado')
  }

  const finalizar = () => {
    const guionId = live.activeGuionId
    setShowName(showLabel)
    const resumen = live.finish()
    if (guionId) updateGuionEstado(guionId, 'Publicado')
    if (resumen) {
      setSummary(resumen)
      addLog('Show finalizado')
      notify('sistema', 'Show finalizado', `Se completaron ${resumen.completed} de ${resumen.total} elementos.`)
    }
    setConfirmFinish(false)
  }

  if (summary) {
    return (
      <div className="relative flex min-h-dvh flex-col overflow-hidden bg-night-950 text-chalk">
        <FieldLines className="pointer-events-none absolute -right-32 -top-24 size-[560px] text-white/[0.05]" />
        <header className="relative z-10 flex items-center justify-between p-5 sm:p-6">
          <Logo tone="light" />
          <ThemeToggle />
        </header>
        <main className="relative z-10 flex flex-1 items-center justify-center px-4 pb-16">
          <div className="w-full max-w-lg rounded-card border border-white/10 bg-white/[0.04] p-8 text-center backdrop-blur-sm">
            <span className="mx-auto grid size-16 place-items-center rounded-full bg-live/15 text-live">
              <CheckCircle2 className="size-7" />
            </span>
            <p className="mt-5 text-[10px] font-bold uppercase tracking-[0.2em] text-live">Transmisión cerrada</p>
            <h1 className="display mt-2 text-4xl font-semibold text-chalk">Show finalizado</h1>
            <p className="mt-2 text-sm text-chalk/55">
              {showName || showLabel} cerró con {summary.completed} de {summary.total} elementos completados.
            </p>
            <div className="mt-6 grid grid-cols-3 gap-2 rounded-card border border-white/10 bg-white/[0.03] p-4 text-center">
              <div>
                <p className="text-[9px] uppercase tracking-wide text-chalk/40">Completados</p>
                <p className="tabular display text-2xl font-semibold text-chalk">{summary.completed}</p>
              </div>
              <div>
                <p className="text-[9px] uppercase tracking-wide text-chalk/40">Elementos</p>
                <p className="tabular display text-2xl font-semibold text-chalk">{summary.total}</p>
              </div>
              <div>
                <p className="text-[9px] uppercase tracking-wide text-chalk/40">Duración</p>
                <p className="tabular font-mono text-lg font-bold text-chalk">{formatElapsed(summary.elapsed)}</p>
              </div>
            </div>
            <div className="mt-6 flex flex-col justify-center gap-2 sm:flex-row">
              <Button variant="live" onClick={() => navigate('/app/guion')} rightIcon={<ArrowRight className="size-4" />}>
                Volver a guiones
              </Button>
              <Button asChild variant="ghost" className="text-chalk hover:bg-white/10">
                <Link to="/app/dashboard">Ir al dashboard</Link>
              </Button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (live.status !== 'live') {
    return (
      <div className="relative flex min-h-dvh flex-col overflow-hidden bg-night-950 text-chalk">
        <FieldLines className="pointer-events-none absolute -right-32 -top-24 size-[560px] text-white/[0.05]" />
        <header className="relative z-10 flex items-center justify-between p-5 sm:p-6">
          <Logo tone="light" />
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button asChild variant="ghost" size="sm" className="text-chalk hover:bg-white/10">
              <Link to="/app/guion">
                <ChevronLeft className="size-4" />
                Guiones
              </Link>
            </Button>
          </div>
        </header>
        <main className="relative z-10 flex flex-1 items-center justify-center px-4 pb-16">
          <div className="w-full max-w-lg rounded-card border border-white/10 bg-white/[0.04] p-8 text-center backdrop-blur-sm">
            <span className="mx-auto grid size-16 place-items-center rounded-full bg-white/[0.06] text-chalk/50">
              <Radio className="size-7" />
            </span>
            <p className="mt-5 text-[10px] font-bold uppercase tracking-[0.2em] text-chalk/40">Control de producción</p>
            <h1 className="display mt-2 text-4xl font-semibold text-chalk">No hay show en vivo</h1>
            <p className="mt-2 text-sm text-chalk/55">
              {publicado
                ? `${publicado.nombre} está publicado y listo para ejecutar.`
                : 'Publica un guion desde el módulo de producción para iniciar la jornada.'}
            </p>
            <div className="mt-6 flex flex-col justify-center gap-2 sm:flex-row">
              {publicado && (
                <Button variant="live" onClick={iniciarDesdeAqui} rightIcon={<ArrowRight className="size-4" />}>
                  Iniciar show
                </Button>
              )}
              <Button asChild variant="ghost" className="text-chalk hover:bg-white/10">
                <Link to="/app/guion">Volver a guiones</Link>
              </Button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="relative min-h-dvh bg-night-950 text-chalk">
      <FieldLines className="pointer-events-none fixed -bottom-40 -right-40 size-[600px] text-white/[0.04]" />

      <header className="relative z-20 flex items-center justify-between gap-3 border-b border-white/10 bg-night-950/80 px-4 py-3 backdrop-blur-md sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <Logo size="sm" withWordmark={false} tone="light" />
          <div className="hidden min-w-0 sm:block">
            <p className="truncate text-xs font-bold text-chalk">{showLabel}</p>
            <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-chalk/40">Control de producción</p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-live/25 bg-live/10 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.12em] text-live">
            <span className="size-1.5 rounded-full bg-live live-dot" />
            En vivo
          </span>
          <span className="tabular hidden font-mono text-sm font-bold text-chalk sm:inline">{formatElapsed(elapsed)}</span>
          <span className="hidden items-center gap-1.5 text-[10px] font-medium text-chalk/45 md:inline-flex">
            <Wifi className="size-3.5 text-live" />
            Sincronizado
          </span>
          <ThemeToggle />
          <Button asChild variant="ghost" size="icon" className="text-chalk hover:bg-white/10">
            <Link to="/app/guion" aria-label="Salir del control">
              <LogOut className="size-4" />
            </Link>
          </Button>
          <Button variant="danger" size="sm" onClick={() => setConfirmFinish(true)}>
            Finalizar
          </Button>
        </div>
      </header>

      <main className="relative z-10 mx-auto w-full max-w-[1440px] px-4 py-5 pb-28 sm:px-6 lg:px-8 lg:py-6 lg:pb-10">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
          <div className="space-y-4 lg:col-span-8">
            <div className="relative overflow-hidden rounded-card border border-white/10 bg-white/[0.04] p-5 backdrop-blur-sm sm:p-6">
              <FieldLines className="pointer-events-none absolute -bottom-32 -right-24 size-[360px] text-white/[0.05]" />
              <div className="relative">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Badge tone="live" dot>En curso</Badge>
                    <Badge tone="neutral">{current?.tipo ?? 'Sin fase'}</Badge>
                    {current?.inning && <Badge tone="time">Inning {current.inning} · {current.medioInning}</Badge>}
                  </div>
                  <span className="font-mono text-xs text-chalk/45">
                    {current?.tipo === 'Juego' ? `Inning ${current.inning}` : formatTime(current?.hora ?? null)}
                  </span>
                </div>

                <h1 className="display mt-4 max-w-3xl text-4xl font-semibold leading-[0.95] text-chalk sm:text-5xl">
                  {current?.contenido ?? 'Sin elemento en curso'}
                </h1>
                <p className="mt-2 text-xs text-chalk/55">
                  Encargado: <strong className="text-chalk/80">{current?.encargado ?? 'Sin asignar'}</strong>
                  {current ? ` · ${formatDuration(current.duracion)} estimados` : ''}
                </p>

                <div className="mt-6 flex flex-wrap items-center gap-6">
                  <div>
                    <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-chalk/40">Tiempo de show</p>
                    <p className="tabular font-mono text-4xl font-bold text-chalk">{formatElapsed(elapsed)}</p>
                  </div>
                  <div className="min-w-48 flex-1">
                    <div className="mb-1.5 flex items-center justify-between text-[10px] text-chalk/45">
                      <span>{live.completedCount} de {live.elements.length} completados</span>
                      <span>{live.progress}%</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-white/10">
                      <div className="h-full rounded-full bg-live transition-[width] duration-500" style={{ width: `${live.progress}%` }} />
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-2 sm:flex-row">
                  <Button
                    variant="ghost"
                    className="h-14 border border-white/10 text-chalk hover:bg-white/10 sm:w-40"
                    onClick={retroceder}
                    disabled={live.currentIndex <= 0}
                    leftIcon={<RotateCcw className="size-5" />}
                  >
                    Retroceder
                  </Button>
                  <button
                    type="button"
                    onClick={handleTap}
                    aria-label="Doble toque para avanzar"
                    className="group flex h-14 flex-1 touch-manipulation items-center justify-center gap-3 rounded-control bg-live px-6 text-sm font-bold text-night-950 transition-transform active:scale-[0.99]"
                  >
                    <span className="grid size-8 place-items-center rounded-full bg-night-950/15">
                      <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                    </span>
                    Avanzar al siguiente
                  </button>
                </div>
                <p className="mt-2 text-center text-[10px] font-medium text-chalk/35">
                  Doble toque o doble clic para avanzar · ↩ para retroceder
                </p>
              </div>
            </div>

            <div className="rounded-card border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">Siguientes en el guion</p>
                <span className="text-[10px] text-chalk/35">{live.pendingCount} pendientes</span>
              </div>
              <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {live.nextElements.length === 0 ? (
                  <p className="col-span-2 rounded-control border border-dashed border-white/10 px-3 py-6 text-center text-xs text-chalk/35">
                    No hay más elementos pendientes.
                  </p>
                ) : (
                  live.nextElements.map((elemento, index) => (
                    <div key={elemento.id} className="flex items-start gap-3 rounded-control border border-white/10 bg-white/[0.03] px-3 py-2.5">
                      <span className="grid size-6 shrink-0 place-items-center rounded-full bg-white/[0.06] text-[10px] font-bold text-chalk/60">
                        {index + 1}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-xs font-semibold text-chalk/85">{elemento.contenido}</p>
                        <p className="text-[10px] text-chalk/40">
                          {elemento.tipo === 'Juego' ? `Inning ${elemento.inning} · ${elemento.medioInning}` : `${elemento.tipo} · ${formatTime(elemento.hora)}`}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="space-y-4 lg:col-span-4">
            <div className="rounded-card border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">Avance del show</p>
                  <p className="mt-1 text-sm font-bold text-chalk">{live.completedCount} de {live.elements.length} elementos</p>
                </div>
                <ProgressRing value={live.progress} size={92} stroke={8} color="var(--live)">
                  <span className="display tabular text-xl font-semibold text-chalk">{live.progress}%</span>
                </ProgressRing>
              </div>
              <InningRibbon
                className="mt-4"
                activeInning={current?.inning ?? null}
                completedInnings={live.elements
                  .filter((elemento) => elemento.tipo === 'Juego' && elemento.estado === 'Completado' && elemento.inning)
                  .map((elemento) => elemento.inning as number)}
              />
            </div>

            <div className="rounded-card border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">Operadores</p>
                <Users className="size-3.5 text-chalk/30" />
              </div>
              <div className="mt-3 space-y-2.5">
                {usuarios
                  .filter((usuario) => usuario.activo)
                  .slice(0, 4)
                  .map((usuario) => (
                    <div key={usuario.id} className="flex items-center gap-2.5">
                      <Avatar name={usuario.nombre} size="sm" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-semibold text-chalk/85">{usuario.nombre}</p>
                        <p className="truncate text-[10px] text-chalk/40">{usuario.departamento}</p>
                      </div>
                      <span className="size-1.5 rounded-full bg-live" />
                    </div>
                  ))}
              </div>
            </div>

            <div className="rounded-card border border-white/10 bg-white/[0.03] p-5">
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">Bitácora del show</p>
              <div className="scroll-area mt-3 max-h-44 space-y-2 overflow-y-auto pr-1">
                {log.map((entry) => (
                  <div key={entry.id} className="flex items-start gap-2 text-[10px]">
                    <span className="font-mono text-chalk/30">{entry.time}</span>
                    <span className="text-chalk/60">{entry.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-card border border-white/10 bg-white/[0.03] p-4">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">Rundown completo</p>
            <span className="text-[10px] text-chalk/35">{live.elements.length} elementos · {live.progress}%</span>
          </div>
          <div className="scroll-area mt-3 flex gap-2 overflow-x-auto pb-1">
            {live.elements.map((elemento, index) => {
              const activo = elemento.estado === 'En curso'
              const completado = elemento.estado === 'Completado'
              return (
                <div
                  key={elemento.id}
                  className={cn(
                    'min-w-[220px] max-w-[240px] shrink-0 rounded-control border p-3',
                    activo
                      ? 'border-time/40 bg-time-soft'
                      : completado
                        ? 'border-live/20 bg-live-soft'
                        : 'border-white/10 bg-white/[0.02]',
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[9px] font-semibold text-chalk/35">
                      {String(index + 1).padStart(2, '0')}
                    </span>
                    <span
                      className={cn(
                        'text-[8px] font-bold uppercase tracking-[0.12em]',
                        activo ? 'text-time' : completado ? 'text-live' : 'text-chalk/30',
                      )}
                    >
                      {elemento.estado}
                    </span>
                  </div>
                  <p className="mt-2 line-clamp-2 text-[11px] font-semibold leading-snug text-chalk/80">
                    {elemento.contenido}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[9px] text-chalk/35">
                    <span>
                      {elemento.tipo === 'Juego'
                        ? `Inning ${elemento.inning} · ${elemento.medioInning}`
                        : elemento.hora}
                    </span>
                    <span>{formatDuration(elemento.duracion)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </main>

      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-white/10 bg-night-950/95 p-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] backdrop-blur-md lg:hidden">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            className="h-12 flex-1 border border-white/10 text-chalk hover:bg-white/10"
            onClick={retroceder}
            disabled={live.currentIndex <= 0}
            leftIcon={<RotateCcw className="size-4" />}
          >
            Atrás
          </Button>
          <button
            type="button"
            onClick={handleTap}
            className="flex h-12 flex-[1.4] touch-manipulation items-center justify-center gap-2 rounded-control bg-live text-xs font-bold text-night-950"
          >
            <ArrowRight className="size-4" />
            Doble toque para avanzar
          </button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmFinish}
        onOpenChange={setConfirmFinish}
        title="Finalizar show"
        description="Se cerrará la ejecución en vivo y el guion volverá al estado publicado."
        confirmLabel="Finalizar show"
        onConfirm={finalizar}
      />
    </div>
  )
}

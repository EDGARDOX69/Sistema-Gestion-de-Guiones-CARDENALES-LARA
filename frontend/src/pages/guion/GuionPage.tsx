import {
  ArrowRight,
  CalendarDays,
  Clock,
  Copy,
  Eye,
  ListChecks,
  Pencil,
  Play,
  Plus,
  Radio,
  Send,
  Trash2,
} from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { FieldLines } from '@/components/brand/FieldLines'
import { InningRibbon } from '@/components/brand/InningRibbon'
import { Badge, type Tone } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Drawer } from '@/components/ui/Drawer'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Progress } from '@/components/ui/Progress'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { useData } from '@/hooks/useData'
import { useLiveClock } from '@/hooks/useLiveClock'
import { useLiveShow } from '@/hooks/useLiveShow'
import {
  ESTADO_ELEMENTO_TONE,
  ESTADO_GUION_TONE,
} from '@/lib/constants'
import { formatDate, formatDuration, formatElapsed, formatTime, nombreCorto } from '@/lib/format'
import { contarFases, duracionGuion, progresoElementos } from '@/lib/selectors'
import type { FaseGuion, Guion } from '@/types'

const FASES: FaseGuion[] = ['Prejuego', 'Juego', 'Postjuego']

export function GuionPage() {
  const navigate = useNavigate()
  const {
    guiones,
    deleteGuion,
    publicarGuion,
    replicarGuion,
    updateGuionEstado,
  } = useData()
  const live = useLiveShow()
  const elapsed = useLiveClock(live.startedAt, live.status === 'live')
  const [selected, setSelected] = useState<Guion | null>(null)
  const [toPublish, setToPublish] = useState<Guion | null>(null)
  const [toDelete, setToDelete] = useState<Guion | null>(null)
  const [replicar, setReplicar] = useState<Guion | null>(null)
  const [nombreCopia, setNombreCopia] = useState('')
  const [fechaCopia, setFechaCopia] = useState('')

  const guionVivo = guiones.find((guion) => guion.id === live.activeGuionId)
  const publicado = guiones.find((guion) => guion.estado === 'Publicado')
  const borradores = guiones.filter((guion) => guion.estado === 'Borrador').length
  const publicados = guiones.filter((guion) => guion.estado === 'Publicado').length

  const iniciarShow = (guion: Guion) => {
    if (live.status === 'live') {
      toast.error('Finaliza el show actual antes de iniciar otro')
      return
    }
    if (guion.elementos.length === 0) {
      toast.error('El guion no tiene elementos para ejecutar')
      return
    }
    live.start(guion.id, guion.elementos)
    updateGuionEstado(guion.id, 'En vivo')
    toast.success('Show iniciado', { description: guion.nombre })
    navigate(`/app/guion/${guion.id}/en-vivo`)
  }

  const abrirReplicar = (guion: Guion) => {
    setReplicar(guion)
    setNombreCopia(`${nombreCorto(guion.nombre)} (copia)`)
    setFechaCopia(guion.fecha)
  }

  const confirmarReplicar = () => {
    if (!replicar) return
    if (!nombreCopia.trim() || !fechaCopia) {
      toast.error('Completa el nombre y la fecha')
      return
    }
    replicarGuion(replicar.id, nombreCopia.trim(), fechaCopia)
    toast.success('Guion replicado')
    setReplicar(null)
  }

  const confirmarPublicar = () => {
    if (!toPublish) return
    publicarGuion(toPublish.id)
    toast.success('Guion publicado')
    setToPublish(null)
  }

  const confirmarEliminar = () => {
    if (!toDelete) return
    deleteGuion(toDelete.id)
    toast.success('Guion eliminado')
    setToDelete(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Módulo de producción"
        title="Guion"
        description="Guiones del juego y control del show en vivo."
        actions={
          <>
            <Button variant="secondary" size="sm" leftIcon={<Radio className="size-3.5" />} onClick={() => navigate(live.status === 'live' ? `/app/guion/${live.activeGuionId ?? 1}/en-vivo` : '/app/guion')} disabled={live.status !== 'live'}>
              Control en vivo
            </Button>
            <Button asChild size="sm" leftIcon={<Plus className="size-3.5" />}>
              <Link to="/app/guion/nuevo">Nuevo guion</Link>
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          { label: 'Guiones', value: String(guiones.length), hint: 'En la temporada', tone: 'brand', icon: ListChecks },
          { label: 'Borradores', value: String(borradores), hint: 'Pendientes de publicar', tone: 'time', icon: Pencil },
          { label: 'Publicados', value: String(publicados), hint: 'Listos para ejecutar', tone: 'info', icon: Send },
          { label: 'Elementos del show', value: String(guionVivo?.elementos.length ?? 0), hint: live.status === 'live' ? 'Show en curso' : 'Sin show activo', tone: 'live', icon: Radio },
        ]}
      />

      <Card className="relative overflow-hidden border-night-800 bg-night-950 p-5 text-chalk sm:p-6">
        <FieldLines className="pointer-events-none absolute -bottom-28 -right-24 size-[380px] text-white/[0.06]" />
        <div className="relative">
          <div className="flex flex-wrap items-center gap-2">
            {live.status === 'live' ? (
              <Badge tone="live" dot>
                Show en vivo
              </Badge>
            ) : (
              <Badge tone="neutral">Show en espera</Badge>
            )}
            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/45">
              {guionVivo ? nombreCorto(guionVivo.nombre) : 'Cardenales vs Leones'}
            </span>
          </div>
          <h2 className="display mt-4 max-w-2xl text-3xl font-semibold text-chalk sm:text-4xl">
            {live.currentElement?.contenido ?? 'El palco está listo para el próximo show.'}
          </h2>
          <p className="mt-2 text-xs text-chalk/55">
            {live.currentElement
              ? `${live.currentElement.tipo}${live.currentElement.inning ? ` · Inning ${live.currentElement.inning} ${live.currentElement.medioInning ?? ''}` : ''} · ${live.currentElement.encargado}`
              : publicado
                ? `${nombreCorto(publicado.nombre)} está publicado y listo para iniciar.`
                : 'Crea y publica un guion para iniciar la ejecución.'}
          </p>

          {live.status === 'live' && (
            <div className="mt-5 flex flex-wrap items-end gap-6">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-chalk/40">Tiempo de show</p>
                <p className="tabular font-mono text-3xl font-bold text-chalk">{formatElapsed(elapsed)}</p>
              </div>
              <div className="min-w-40 flex-1">
                <div className="mb-1.5 flex items-center justify-between text-[10px] text-chalk/50">
                  <span>{live.completedCount} de {live.elements.length} completados</span>
                  <span>{live.progress}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-live transition-[width] duration-500" style={{ width: `${live.progress}%` }} />
                </div>
              </div>
            </div>
          )}

          <div className="mt-5 flex flex-wrap gap-2">
            {live.status === 'live' ? (
              <Button asChild variant="live" size="sm">
                <Link to={`/app/guion/${live.activeGuionId ?? 1}/en-vivo`}>
                  Abrir control
                  <ArrowRight className="size-3.5" />
                </Link>
              </Button>
            ) : (
              publicado && (
                <Button variant="live" size="sm" onClick={() => iniciarShow(publicado)} leftIcon={<Play className="size-3.5" />}>
                  Iniciar show
                </Button>
              )
            )}
            <Button asChild variant="ghost" size="sm" className="text-chalk hover:bg-white/10 hover:text-chalk">
              <Link to="/app/guion/nuevo" className="inline-flex items-center gap-2">
                <Plus className="size-3.5" />
                Nuevo guion
              </Link>
            </Button>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="space-y-3 lg:col-span-8">
          {guiones.map((guion) => {
            const duracion = duracionGuion(guion.elementos)
            const fases = contarFases(guion.elementos)
            const pct = progresoElementos(guion.elementos)
            const enVivo = guion.estado === 'En vivo'
            return (
              <Card key={guion.id} className="p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Badge tone={(ESTADO_GUION_TONE[guion.estado] ?? 'neutral') as Tone} dot size="sm">
                        {guion.estado}
                      </Badge>
                      {enVivo && (
                        <Badge tone="live" size="sm">
                          En ejecución
                        </Badge>
                      )}
                    </div>
                    <p className="mt-2 text-sm font-bold text-ink">{nombreCorto(guion.nombre)}</p>
                    <p className="mt-0.5 text-[11px] text-ink-muted">
                      {formatDate(guion.fecha)} · {guion.tiempoInning} min por inning · modificado {formatDate(guion.modificado)}
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" aria-label="Ver detalle" onClick={() => setSelected(guion)}>
                    <Eye className="size-4" />
                  </Button>
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[10px] text-ink-muted">
                  <span className="inline-flex items-center gap-1"><ListChecks className="size-3" /> {guion.elementos.length} elementos</span>
                  <span className="inline-flex items-center gap-1"><Clock className="size-3" /> {formatDuration(duracion)}</span>
                  <span className="inline-flex items-center gap-1"><CalendarDays className="size-3" /> {fases.prejuego} pre · {fases.juego} juego · {fases.postjuego} post</span>
                </div>

                <div className="mt-3">
                  <div className="mb-1.5 flex items-center justify-between text-[10px] text-ink-muted">
                    <span>Progreso del guion</span>
                    <span>{pct}%</span>
                  </div>
                  <Progress value={pct} tone={enVivo ? 'live' : 'brand'} size="sm" />
                </div>

                <div className="mt-3 flex flex-wrap items-center justify-end gap-1.5 border-t border-line pt-3">
                  {enVivo && (
                    <Button asChild variant="live" size="sm" leftIcon={<Radio className="size-3.5" />}>
                      <Link to={`/app/guion/${guion.id}/en-vivo`}>Abrir control</Link>
                    </Button>
                  )}
                  {guion.estado === 'Publicado' && (
                    <Button variant="secondary" size="sm" leftIcon={<Play className="size-3.5" />} onClick={() => iniciarShow(guion)}>
                      Iniciar
                    </Button>
                  )}
                  {guion.estado === 'Borrador' && (
                    <Button variant="secondary" size="sm" leftIcon={<Send className="size-3.5" />} onClick={() => setToPublish(guion)}>
                      Publicar
                    </Button>
                  )}
                  {!enVivo && (
                    <Button asChild variant="ghost" size="sm" leftIcon={<Pencil className="size-3.5" />}>
                      <Link to={`/app/guion/${guion.id}/editar`}>Editar</Link>
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" leftIcon={<Copy className="size-3.5" />} onClick={() => abrirReplicar(guion)}>
                    Replicar
                  </Button>
                  <Button variant="ghost" size="icon" aria-label="Eliminar guion" onClick={() => setToDelete(guion)}>
                    <Trash2 className="size-3.5 text-danger" />
                  </Button>
                </div>
              </Card>
            )
          })}
        </div>

        <div className="space-y-4 lg:col-span-4">
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <p className="eyebrow">Agenda</p>
              <CalendarDays className="size-4 text-ink-faint" />
            </div>
            <div className="mt-3 space-y-2">
              {[...guiones]
                .sort((a, b) => a.fecha.localeCompare(b.fecha))
                .map((guion) => (
                  <div key={guion.id} className="flex items-center gap-3 rounded-control border border-line bg-sunken/35 px-3 py-2">
                    <div className="grid size-9 shrink-0 place-items-center rounded-control bg-surface text-center">
                      <span className="text-[10px] font-bold text-ink">{formatDate(guion.fecha).split(' ')[0]}</span>
                      <span className="text-[8px] uppercase text-ink-muted">{formatDate(guion.fecha).split(' ')[1]}</span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-[11px] font-semibold text-ink">{nombreCorto(guion.nombre)}</p>
                      <p className="text-[10px] text-ink-muted">{guion.elementos.length} elementos</p>
                    </div>
                    <Badge tone={(ESTADO_GUION_TONE[guion.estado] ?? 'neutral') as Tone} size="sm">
                      {guion.estado}
                    </Badge>
                  </div>
                ))}
            </div>
          </Card>

          <Card className="p-5">
            <p className="eyebrow">Estado del show</p>
            {live.status === 'live' ? (
              <>
                <div className="mt-3 flex items-center justify-between">
                  <p className="text-sm font-bold text-ink">{live.currentElement?.contenido ?? 'Sin elemento actual'}</p>
                  <Badge tone="live" dot size="sm">En vivo</Badge>
                </div>
                <p className="mt-1 text-[10px] text-ink-muted">
                  {live.completedCount} de {live.elements.length} completados · {live.progress}%
                </p>
                <Progress value={live.progress} tone="live" size="sm" className="mt-2" />
                <InningRibbon
                  className="mt-4"
                  activeInning={live.currentElement?.inning ?? null}
                  completedInnings={live.elements
                    .filter((elemento) => elemento.tipo === 'Juego' && elemento.estado === 'Completado' && elemento.inning)
                    .map((elemento) => elemento.inning as number)}
                />
                <Button asChild variant="live" size="sm" className="mt-4 w-full">
                  <Link to={`/app/guion/${live.activeGuionId ?? 1}/en-vivo`}>Abrir control</Link>
                </Button>
              </>
            ) : (
              <div className="mt-3 rounded-control border border-dashed border-line-strong px-3 py-6 text-center">
                <Radio className="mx-auto size-5 text-ink-faint" />
                <p className="mt-2 text-xs font-semibold text-ink">Sin show activo</p>
                <p className="mt-1 text-[10px] text-ink-muted">
                  {publicado ? 'Hay un guion publicado listo para iniciar.' : 'Publica un guion para iniciar la jornada.'}
                </p>
                {publicado && (
                  <Button variant="secondary" size="sm" className="mt-3" onClick={() => iniciarShow(publicado)} leftIcon={<Play className="size-3.5" />}>
                    Iniciar show
                  </Button>
                )}
              </div>
            )}
          </Card>
        </div>
      </div>

      <Drawer
        open={Boolean(selected)}
        onOpenChange={(open) => !open && setSelected(null)}
        title={selected ? nombreCorto(selected.nombre) : 'Guion'}
        description={selected ? `${formatDate(selected.fecha)} · ${selected.estado}` : undefined}
        width="lg"
        footer={
          selected && (
            <>
              <Button variant="ghost" onClick={() => setSelected(null)}>Cerrar</Button>
              {selected.estado !== 'En vivo' && (
                <Button asChild leftIcon={<Pencil className="size-4" />}>
                  <Link to={`/app/guion/${selected.id}/editar`}>Editar guion</Link>
                </Button>
              )}
            </>
          )
        }
      >
        {selected && (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={(ESTADO_GUION_TONE[selected.estado] ?? 'neutral') as Tone} dot>
                {selected.estado}
              </Badge>
              <Badge tone="info">{selected.elementos.length} elementos</Badge>
              <Badge tone="time">{formatDuration(duracionGuion(selected.elementos))}</Badge>
            </div>

            {live.status === 'live' && selected.id === live.activeGuionId && (
              <InningRibbon
                activeInning={live.currentElement?.inning ?? null}
                completedInnings={selected.elementos
                  .filter((elemento) => elemento.tipo === 'Juego' && elemento.estado === 'Completado' && elemento.inning)
                  .map((elemento) => elemento.inning as number)}
              />
            )}

            {FASES.map((fase) => {
              const elementos = selected.elementos.filter((elemento) => elemento.tipo === fase)
              if (elementos.length === 0) return null
              return (
                <div key={fase}>
                  <div className="mb-2 flex items-center justify-between">
                    <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-ink-muted">{fase}</p>
                    <span className="text-[10px] text-ink-faint">{elementos.length} elementos</span>
                  </div>
                  <div className="space-y-1.5">
                    {elementos.map((elemento) => (
                      <div key={elemento.id} className="flex items-start gap-3 rounded-control border border-line px-3 py-2">
                        <div className="w-16 shrink-0">
                          <p className="font-mono text-[10px] font-semibold text-ink-soft">
                            {elemento.tipo === 'Juego' ? `Inn ${elemento.inning}` : formatTime(elemento.hora)}
                          </p>
                          <p className="text-[9px] text-ink-faint">
                            {elemento.tipo === 'Juego' ? elemento.medioInning : formatDuration(elemento.duracion)}
                          </p>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-ink">{elemento.contenido}</p>
                          <p className="text-[10px] text-ink-muted">{elemento.encargado} · {formatDuration(elemento.duracion)}</p>
                        </div>
                        <Badge tone={(ESTADO_ELEMENTO_TONE[elemento.estado] ?? 'neutral') as Tone} size="sm">
                          {elemento.estado}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Drawer>

      <Modal
        open={Boolean(replicar)}
        onOpenChange={(open) => !open && setReplicar(null)}
        title="Replicar guion"
        description="Crea una copia editable con un nuevo nombre y fecha."
        icon={Copy}
        footer={
          <>
            <Button variant="ghost" onClick={() => setReplicar(null)}>Cancelar</Button>
            <Button onClick={confirmarReplicar} leftIcon={<Copy className="size-4" />}>Replicar guion</Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input label="Nombre del nuevo guion" value={nombreCopia} onChange={(event) => setNombreCopia(event.target.value)} />
          <Input label="Fecha" type="date" value={fechaCopia} onChange={(event) => setFechaCopia(event.target.value)} />
          <p className="text-[11px] text-ink-muted">
            Se copiarán {replicar?.elementos.length ?? 0} elementos en estado pendiente.
          </p>
        </div>
      </Modal>

      <ConfirmDialog
        open={Boolean(toPublish)}
        onOpenChange={(open) => !open && setToPublish(null)}
        title="Publicar guion"
        description={toPublish ? `"${toPublish.nombre}" quedará visible para todo el equipo.` : ''}
        confirmLabel="Publicar"
        onConfirm={confirmarPublicar}
      />
      <ConfirmDialog
        open={Boolean(toDelete)}
        onOpenChange={(open) => !open && setToDelete(null)}
        title="Eliminar guion"
        description={toDelete ? `Se eliminará "${toDelete.nombre}" y sus elementos.` : ''}
        confirmLabel="Eliminar"
        onConfirm={confirmarEliminar}
      />
    </div>
  )
}

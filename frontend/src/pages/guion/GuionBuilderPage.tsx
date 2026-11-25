import { zodResolver } from '@hookform/resolvers/zod'
import {
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  Clock,
  ListChecks,
  Plus,
  Save,
  Trash2,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Badge, type Tone } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input, Textarea } from '@/components/ui/Input'
import { PageHeader } from '@/components/ui/PageHeader'
import { Progress } from '@/components/ui/Progress'
import { Select } from '@/components/ui/Select'
import { useData } from '@/hooks/useData'
import { useSession } from '@/hooks/useSession'
import { formatDate, formatDuration } from '@/lib/format'
import {
  elementoGuionSchema,
  guionSchema,
  type ElementoGuionForm,
  type GuionForm,
} from '@/lib/schemas'
import { contarFases, duracionGuion } from '@/lib/selectors'
import type { ElementoGuion, FaseGuion, MedioInning } from '@/types'

const FASES: FaseGuion[] = ['Prejuego', 'Juego', 'Postjuego']

const FASE_TONE: Record<FaseGuion, Tone> = {
  Prejuego: 'info',
  Juego: 'brand',
  Postjuego: 'time',
}

export function GuionBuilderPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { guiones, usuarios, saveGuion } = useData()
  const { user } = useSession()
  const guion = id ? guiones.find((item) => String(item.id) === id) : undefined
  const [elementos, setElementos] = useState<ElementoGuion[]>(guion?.elementos ?? [])

  const mainForm = useForm<GuionForm>({
    resolver: zodResolver(guionSchema),
    defaultValues: {
      nombre: guion?.nombre ?? '',
      fecha: guion?.fecha ?? '2026-07-10',
      tiempoInning: guion?.tiempoInning ?? 120,
    },
  })

  const elementForm = useForm<ElementoGuionForm>({
    resolver: zodResolver(elementoGuionSchema),
    defaultValues: {
      tipo: 'Juego',
      hora: '18:00',
      inning: 1,
      medioInning: 'Baja',
      contenido: '',
      duracion: 30,
      encargado: user?.nombre ?? 'Keiver',
    },
  })

  const tipo = elementForm.watch('tipo')
  const nombre = mainForm.watch('nombre')
  const fecha = mainForm.watch('fecha')
  const tiempoInning = mainForm.watch('tiempoInning')

  useEffect(() => {
    if (!guion) return
    mainForm.reset({ nombre: guion.nombre, fecha: guion.fecha, tiempoInning: guion.tiempoInning })
    setElementos(guion.elementos)
  }, [guion, mainForm])

  if (id && !guion) {
    return (
      <EmptyState
        icon={ListChecks}
        title="Guion no encontrado"
        description="El guion solicitado no existe o fue eliminado."
        action={<Button asChild><Link to="/app/guion">Volver a guiones</Link></Button>}
      />
    )
  }

  const agregarElemento = (values: ElementoGuionForm) => {
    const mismoTipo = elementos.filter((elemento) => elemento.tipo === values.tipo).length
    const nuevo: ElementoGuion = {
      id: Date.now(),
      tipo: values.tipo,
      hora: values.tipo === 'Juego' ? null : values.hora,
      inning: values.tipo === 'Juego' ? values.inning : null,
      medioInning: values.tipo === 'Juego' ? (values.medioInning as MedioInning) : null,
      contenido: values.contenido,
      duracion: values.duracion,
      encargado: values.encargado,
      orden: mismoTipo + 1,
      estado: 'Pendiente',
    }
    setElementos((prev) => [...prev, nuevo])
    toast.success('Elemento agregado')
    elementForm.reset({
      tipo: values.tipo,
      hora: '18:00',
      inning: 1,
      medioInning: 'Baja',
      contenido: '',
      duracion: 30,
      encargado: values.encargado,
    })
  }

  const quitarElemento = (idElemento: number) => {
    setElementos((prev) => prev.filter((elemento) => elemento.id !== idElemento))
    toast.success('Elemento eliminado')
  }

  const guardar = async () => {
    const valido = await mainForm.trigger()
    if (!valido) {
      toast.error('Completa los datos del guion')
      return
    }
    if (elementos.length === 0) {
      toast.error('Agrega al menos un elemento al guion')
      return
    }
    const values = mainForm.getValues()
    saveGuion(
      {
        nombre: values.nombre,
        fecha: values.fecha,
        tiempoInning: values.tiempoInning,
        elementos,
      },
      guion?.id,
    )
    toast.success(guion ? 'Guion actualizado' : 'Guion registrado')
    navigate('/app/guion')
  }

  const fases = contarFases(elementos)
  const duracion = duracionGuion(elementos)
  const encargados = usuarios
    .filter((usuario) => usuario.activo)
    .map((usuario) => ({ value: usuario.nombre, label: `${usuario.nombre} · ${usuario.rol}` }))

  return (
    <div className="space-y-6">
      <Link to="/app/guion" className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted transition-colors hover:text-ink">
        <ArrowLeft className="size-3.5" />
        Volver a guiones
      </Link>

      <PageHeader
        eyebrow="Módulo de producción"
        title={guion ? 'Editar guion' : 'Nuevo guion'}
        description="Define los datos del juego y construye la secuencia de elementos."
        actions={
          <>
            <Button asChild variant="ghost" size="sm">
              <Link to="/app/guion">Cancelar</Link>
            </Button>
            <Button size="sm" leftIcon={<Save className="size-3.5" />} onClick={guardar}>
              Guardar guion
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="space-y-4 lg:col-span-7">
          <Card className="p-5">
            <div className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-control bg-brand-soft text-brand">
                <ListChecks className="size-4" />
              </span>
              <div>
                <p className="text-sm font-bold text-ink">Datos del guion</p>
                <p className="text-[10px] text-ink-muted">Nombre, fecha de juego y tiempo por inning.</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input label="Nombre del guion" placeholder="Ej: Cardenales vs Leones" error={mainForm.formState.errors.nombre?.message} className="sm:col-span-2" {...mainForm.register('nombre')} />
              <Input label="Fecha del juego" type="date" error={mainForm.formState.errors.fecha?.message} {...mainForm.register('fecha')} />
              <Input label="Tiempo por inning (min)" type="number" min={1} error={mainForm.formState.errors.tiempoInning?.message} {...mainForm.register('tiempoInning', { valueAsNumber: true })} />
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-control bg-time-soft text-time">
                <Plus className="size-4" />
              </span>
              <div>
                <p className="text-sm font-bold text-ink">Agregar elemento</p>
                <p className="text-[10px] text-ink-muted">Se agregará al final de la fase seleccionada.</p>
              </div>
            </div>

            <form onSubmit={elementForm.handleSubmit(agregarElemento)} className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
              <Controller
                control={elementForm.control}
                name="tipo"
                render={({ field }) => (
                  <Select
                    label="Fase"
                    options={FASES.map((fase) => ({ value: fase, label: fase }))}
                    value={field.value}
                    onValueChange={field.onChange}
                    error={elementForm.formState.errors.tipo?.message}
                  />
                )}
              />
              {tipo === 'Juego' ? (
                <>
                  <Input label="Inning" type="number" min={1} max={9} error={elementForm.formState.errors.inning?.message} {...elementForm.register('inning', { valueAsNumber: true })} />
                  <Controller
                    control={elementForm.control}
                    name="medioInning"
                    render={({ field }) => (
                      <Select
                        label="Mitad del inning"
                        options={[{ value: 'Alta', label: 'Alta' }, { value: 'Baja', label: 'Baja' }]}
                        value={field.value}
                        onValueChange={field.onChange}
                        error={elementForm.formState.errors.medioInning?.message}
                      />
                    )}
                  />
                </>
              ) : (
                <Input label="Hora" type="time" error={elementForm.formState.errors.hora?.message} {...elementForm.register('hora')} />
              )}
              <Input label="Duración (segundos)" type="number" min={1} error={elementForm.formState.errors.duracion?.message} {...elementForm.register('duracion', { valueAsNumber: true })} />
              <Controller
                control={elementForm.control}
                name="encargado"
                render={({ field }) => (
                  <Select
                    label="Encargado"
                    options={encargados}
                    value={field.value}
                    onValueChange={field.onChange}
                    error={elementForm.formState.errors.encargado?.message}
                  />
                )}
              />
              <Textarea label="Contenido" placeholder="Describe la actividad o pauta..." error={elementForm.formState.errors.contenido?.message} className="sm:col-span-2" {...elementForm.register('contenido')} />
              <div className="sm:col-span-2">
                <Button type="submit" variant="secondary" className="w-full" leftIcon={<Plus className="size-4" />}>
                  Agregar elemento
                </Button>
              </div>
            </form>
          </Card>
        </div>

        <div className="lg:col-span-5">
          <Card className="sticky top-20 overflow-hidden">
            <div className="border-b border-line bg-sunken/35 p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="eyebrow">Vista previa</p>
                  <p className="mt-1 truncate text-sm font-bold text-ink">{nombre || 'Guion sin nombre'}</p>
                  <p className="mt-0.5 flex items-center gap-1.5 text-[10px] text-ink-muted">
                    <CalendarDays className="size-3" />
                    {fecha ? formatDate(fecha) : 'Sin fecha'} · {tiempoInning || 0} min por inning
                  </p>
                </div>
                <Badge tone="neutral">{elementos.length} elementos</Badge>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div><p className="text-[9px] uppercase tracking-wide text-ink-muted">Pre</p><p className="text-sm font-bold text-ink">{fases.prejuego}</p></div>
                <div><p className="text-[9px] uppercase tracking-wide text-ink-muted">Juego</p><p className="text-sm font-bold text-ink">{fases.juego}</p></div>
                <div><p className="text-[9px] uppercase tracking-wide text-ink-muted">Post</p><p className="text-sm font-bold text-ink">{fases.postjuego}</p></div>
              </div>
              <div className="mt-3 flex items-center justify-between text-[10px] text-ink-muted">
                <span className="inline-flex items-center gap-1"><Clock className="size-3" /> Duración total</span>
                <span className="tabular font-semibold text-ink">{formatDuration(duracion)}</span>
              </div>
              <Progress value={Math.min(100, elementos.length * 6)} tone="brand" size="sm" className="mt-2" />
            </div>

            <div className="max-h-[520px] overflow-y-auto p-4 scroll-area">
              {elementos.length === 0 ? (
                <div className="rounded-control border border-dashed border-line-strong px-3 py-8 text-center">
                  <AlertTriangle className="mx-auto size-5 text-ink-faint" />
                  <p className="mt-2 text-xs font-semibold text-ink">Sin elementos</p>
                  <p className="mt-1 text-[10px] text-ink-muted">Agrega el primer elemento para ver la secuencia aquí.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {FASES.map((fase) => {
                    const delFase = elementos.filter((elemento) => elemento.tipo === fase)
                    if (delFase.length === 0) return null
                    return (
                      <div key={fase}>
                        <div className="mb-1.5 flex items-center justify-between">
                          <Badge tone={FASE_TONE[fase]} size="sm">{fase}</Badge>
                          <span className="text-[9px] text-ink-faint">{delFase.length}</span>
                        </div>
                        <div className="space-y-1.5">
                          {delFase.map((elemento) => (
                            <div key={elemento.id} className="group flex items-start gap-2 rounded-control border border-line bg-surface px-2.5 py-2">
                              <div className="w-12 shrink-0">
                                <p className="font-mono text-[9px] font-semibold text-ink-soft">
                                  {elemento.tipo === 'Juego' ? `Inn ${elemento.inning}` : elemento.hora}
                                </p>
                                <p className="text-[8px] text-ink-faint">{formatDuration(elemento.duracion)}</p>
                              </div>
                              <div className="min-w-0 flex-1">
                                <p className="text-[11px] font-semibold leading-snug text-ink">{elemento.contenido}</p>
                                <p className="text-[9px] text-ink-muted">{elemento.encargado}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => quitarElemento(elemento.id)}
                                aria-label="Quitar elemento"
                                className="grid size-6 shrink-0 place-items-center rounded text-ink-faint opacity-0 transition-opacity hover:bg-danger-soft hover:text-danger group-hover:opacity-100"
                              >
                                <Trash2 className="size-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            <div className="border-t border-line p-4">
              <Button className="w-full" onClick={guardar} leftIcon={<Save className="size-4" />}>
                {guion ? 'Guardar cambios' : 'Finalizar guion'}
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

import { zodResolver } from '@hookform/resolvers/zod'
import {
  Armchair,
  Boxes,
  Camera,
  Eye,
  Guitar,
  Lightbulb,
  Mic,
  Monitor,
  Package,
  Pencil,
  Plus,
  RotateCcw,
  Tags,
  Trash2,
  Truck,
  UserRound,
  Wrench,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Avatar } from '@/components/ui/Avatar'
import { Badge, type Tone } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Drawer } from '@/components/ui/Drawer'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input, Textarea } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SearchInput } from '@/components/ui/SearchInput'
import { Select } from '@/components/ui/Select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { useData } from '@/hooks/useData'
import { ESTADO_RECURSO_OPTIONS, ESTADO_RECURSO_TONE } from '@/lib/constants'
import { formatDate, formatMoney } from '@/lib/format'
import {
  asignacionSchema,
  recursoSchema,
  tipoRecursoSchema,
  type AsignacionForm,
  type RecursoForm,
  type TipoRecursoForm,
} from '@/lib/schemas'
import { recursosPorEstado } from '@/lib/selectors'
import type { Asignacion, Recurso, TipoRecurso } from '@/types'

const TIPO_VISUAL: Record<number, { icon: LucideIcon; className: string }> = {
  1: { icon: Monitor, className: 'bg-info-soft text-info' },
  2: { icon: Camera, className: 'bg-brand-soft text-brand' },
  3: { icon: Lightbulb, className: 'bg-time-soft text-time' },
  4: { icon: Armchair, className: 'bg-live-soft text-live' },
  5: { icon: Guitar, className: 'bg-time-soft text-time' },
  6: { icon: Truck, className: 'bg-info-soft text-info' },
  7: { icon: Package, className: 'bg-sunken text-ink-soft' },
  8: { icon: Mic, className: 'bg-brand-soft text-brand' },
}

const ESTADO_ASIGNACION_TONE: Record<string, Tone> = {
  Pendiente: 'time',
  Devuelto: 'live',
  Vencido: 'danger',
}

function RecursoFormModal({
  open,
  onOpenChange,
  recurso,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  recurso: Recurso | null
}) {
  const { tiposRecurso, saveRecurso } = useData()
  const form = useForm<RecursoForm>({
    resolver: zodResolver(recursoSchema),
    defaultValues: {
      nombre: recurso?.nombre ?? '',
      tipoId: recurso ? String(recurso.tipoId) : '',
      descripcion: recurso?.descripcion ?? '',
      fechaCompra: recurso?.fechaCompra ?? '2026-07-10',
      costo: recurso?.costo ?? 0,
      estado: recurso?.estado ?? 'Disponible',
    },
  })

  const onSubmit = (values: RecursoForm) => {
    saveRecurso(
      {
        nombre: values.nombre,
        descripcion: values.descripcion,
        tipoId: Number(values.tipoId),
        estado: values.estado as Recurso['estado'],
        fechaCompra: values.fechaCompra,
        costo: values.costo,
      },
      recurso?.id,
    )
    toast.success(recurso ? 'Recurso actualizado' : 'Recurso registrado')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={recurso ? 'Editar recurso' : 'Nuevo recurso'}
      description="Equipo o material del inventario operativo."
      icon={Boxes}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {recurso ? 'Guardar cambios' : 'Registrar recurso'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
        <Input label="Nombre del recurso" placeholder="Ej: Sony PXW-Z150" error={form.formState.errors.nombre?.message} className="sm:col-span-2" {...form.register('nombre')} />
        <Controller
          control={form.control}
          name="tipoId"
          render={({ field }) => (
            <Select
              label="Tipo"
              placeholder="Selecciona un tipo"
              options={tiposRecurso.map((tipo) => ({ value: String(tipo.id), label: tipo.nombre }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.tipoId?.message}
            />
          )}
        />
        <Controller
          control={form.control}
          name="estado"
          render={({ field }) => (
            <Select
              label="Estado"
              options={ESTADO_RECURSO_OPTIONS}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.estado?.message}
            />
          )}
        />
        <Input label="Fecha de compra" type="date" error={form.formState.errors.fechaCompra?.message} {...form.register('fechaCompra')} />
        <Input label="Costo" type="number" min={0} step="0.01" placeholder="0.00" error={form.formState.errors.costo?.message} {...form.register('costo', { valueAsNumber: true })} />
        <Textarea label="Descripción" placeholder="Detalle del recurso..." className="sm:col-span-2" error={form.formState.errors.descripcion?.message} {...form.register('descripcion')} />
      </form>
    </Modal>
  )
}

function TipoFormModal({
  open,
  onOpenChange,
  tipo,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  tipo: TipoRecurso | null
}) {
  const { saveTipoRecurso } = useData()
  const form = useForm<TipoRecursoForm>({
    resolver: zodResolver(tipoRecursoSchema),
    defaultValues: {
      nombre: tipo?.nombre ?? '',
      descripcion: tipo?.descripcion ?? '',
    },
  })

  const onSubmit = (values: TipoRecursoForm) => {
    saveTipoRecurso(values, tipo?.id)
    toast.success(tipo ? 'Tipo actualizado' : 'Tipo registrado')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={tipo ? 'Editar tipo' : 'Nuevo tipo de recurso'}
      description="Categoría para clasificar los recursos del inventario."
      icon={Tags}
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {tipo ? 'Guardar cambios' : 'Registrar tipo'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <Input label="Nombre" placeholder="Ej: Equipo de Audio" error={form.formState.errors.nombre?.message} {...form.register('nombre')} />
        <Textarea label="Descripción" placeholder="Descripción del tipo..." error={form.formState.errors.descripcion?.message} {...form.register('descripcion')} />
      </form>
    </Modal>
  )
}

function AsignacionFormModal({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { recursos, usuarios, addAsignacion } = useData()
  const form = useForm<AsignacionForm>({
    resolver: zodResolver(asignacionSchema),
    defaultValues: {
      recursoId: '',
      usuarioId: '',
      fechaDevolucion: '2026-07-12',
      notas: '',
    },
  })

  const onSubmit = (values: AsignacionForm) => {
    const result = addAsignacion({
      recursoId: Number(values.recursoId),
      usuarioId: Number(values.usuarioId),
      fechaDevolucionEsperada: values.fechaDevolucion,
      notas: values.notas,
    })
    if (!result.ok) {
      toast.error(result.error ?? 'No se pudo asignar el recurso')
      return
    }
    toast.success('Recurso asignado')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Nueva asignación"
      description="Entrega un recurso disponible a un miembro del equipo."
      icon={UserRound}
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            Asignar recurso
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <Controller
          control={form.control}
          name="recursoId"
          render={({ field }) => (
            <Select
              label="Recurso disponible"
              placeholder="Selecciona un recurso"
              options={recursos
                .filter((recurso) => recurso.estado === 'Disponible')
                .map((recurso) => ({ value: String(recurso.id), label: recurso.nombre }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.recursoId?.message}
            />
          )}
        />
        <Controller
          control={form.control}
          name="usuarioId"
          render={({ field }) => (
            <Select
              label="Usuario"
              placeholder="Selecciona un usuario"
              options={usuarios
                .filter((usuario) => usuario.activo)
                .map((usuario) => ({ value: String(usuario.id), label: `${usuario.nombre} · ${usuario.departamento}` }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.usuarioId?.message}
            />
          )}
        />
        <Input label="Devolución esperada" type="date" error={form.formState.errors.fechaDevolucion?.message} {...form.register('fechaDevolucion')} />
        <Textarea label="Notas" placeholder="Detalle de la asignación..." error={form.formState.errors.notas?.message} {...form.register('notas')} />
      </form>
    </Modal>
  )
}

export function InventarioPage() {
  const {
    recursos,
    tiposRecurso,
    asignaciones,
    usuarios,
    deleteRecurso,
    deleteTipoRecurso,
    devolverAsignacion,
  } = useData()
  const [searchParams, setSearchParams] = useSearchParams()
  const [tab, setTab] = useState('recursos')
  const [search, setSearch] = useState('')
  const [tipoFilter, setTipoFilter] = useState('all')
  const [estadoFilter, setEstadoFilter] = useState('all')
  const [recursoOpen, setRecursoOpen] = useState(() => searchParams.get('nuevo') === '1')
  const [editing, setEditing] = useState<Recurso | null>(null)
  const [tipoOpen, setTipoOpen] = useState(false)
  const [editingTipo, setEditingTipo] = useState<TipoRecurso | null>(null)
  const [asignacionOpen, setAsignacionOpen] = useState(false)
  const [detail, setDetail] = useState<Recurso | null>(null)
  const [toDelete, setToDelete] = useState<Recurso | null>(null)
  const [toDeleteTipo, setToDeleteTipo] = useState<TipoRecurso | null>(null)
  const [toDevolver, setToDevolver] = useState<Asignacion | null>(null)

  const cerrarRecurso = (open: boolean) => {
    setRecursoOpen(open)
    if (!open && searchParams.get('nuevo')) setSearchParams({}, { replace: true })
  }

  const resumen = recursosPorEstado(recursos)
  const nombreTipo = (id: number) => tiposRecurso.find((tipo) => tipo.id === id)?.nombre ?? 'Sin tipo'
  const nombreUsuario = (id: number) => usuarios.find((usuario) => usuario.id === id)?.nombre ?? 'Sin usuario'

  const filtrados = useMemo(() => {
    const term = search.trim().toLowerCase()
    return recursos.filter((recurso) => {
      const coincideTexto = !term || recurso.nombre.toLowerCase().includes(term) || recurso.descripcion.toLowerCase().includes(term)
      const coincideTipo = tipoFilter === 'all' || String(recurso.tipoId) === tipoFilter
      const coincideEstado = estadoFilter === 'all' || recurso.estado === estadoFilter
      return coincideTexto && coincideTipo && coincideEstado
    })
  }, [recursos, search, tipoFilter, estadoFilter])

  const abrirNuevo = () => {
    setEditing(null)
    setRecursoOpen(true)
  }

  const abrirEditar = (recurso: Recurso) => {
    setDetail(null)
    setEditing(recurso)
    setRecursoOpen(true)
  }

  const confirmarEliminar = () => {
    if (!toDelete) return
    deleteRecurso(toDelete.id)
    toast.success('Recurso eliminado')
    setToDelete(null)
  }

  const confirmarEliminarTipo = () => {
    if (!toDeleteTipo) return
    const result = deleteTipoRecurso(toDeleteTipo.id)
    if (!result.ok) {
      toast.error(result.error ?? 'No se pudo eliminar el tipo')
    } else {
      toast.success('Tipo eliminado')
    }
    setToDeleteTipo(null)
  }

  const confirmarDevolucion = () => {
    if (!toDevolver) return
    devolverAsignacion(toDevolver.id)
    toast.success('Recurso devuelto al inventario')
    setToDevolver(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Módulo de recursos"
        title="Inventario"
        description="Recursos, tipos y asignaciones del equipo de operaciones."
        actions={
          <>
            <Button variant="secondary" size="sm" leftIcon={<UserRound className="size-3.5" />} onClick={() => setAsignacionOpen(true)}>
              Asignar recurso
            </Button>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={abrirNuevo}>
              Nuevo recurso
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          { label: 'Recursos', value: String(resumen.total), hint: 'En el inventario', tone: 'info', icon: Boxes },
          { label: 'Disponibles', value: String(resumen.disponibles), hint: 'Listos para asignar', tone: 'live', icon: Package },
          { label: 'Asignados', value: String(resumen.asignados), hint: 'En uso por el equipo', tone: 'brand', icon: UserRound },
          { label: 'Valor total', value: formatMoney(resumen.valor), hint: `${resumen.mantenimiento} en mantenimiento`, tone: 'time', icon: Wrench },
        ]}
      />

      <Tabs value={tab} onValueChange={setTab}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <TabsList>
            <TabsTrigger value="recursos">Recursos</TabsTrigger>
            <TabsTrigger value="tipos">Tipos</TabsTrigger>
            <TabsTrigger value="asignaciones">Asignaciones</TabsTrigger>
          </TabsList>
          <div className="flex items-center gap-2">
            <SearchInput value={search} onChange={setSearch} placeholder="Buscar recurso" className="sm:w-64" />
          </div>
        </div>

        <TabsContent value="recursos">
          <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center">
            <Select
              options={[{ value: 'all', label: 'Todos los tipos' }, ...tiposRecurso.map((tipo) => ({ value: String(tipo.id), label: tipo.nombre }))]}
              value={tipoFilter}
              onValueChange={setTipoFilter}
              className="sm:w-52"
            />
            <Select
              options={[{ value: 'all', label: 'Todos los estados' }, ...ESTADO_RECURSO_OPTIONS]}
              value={estadoFilter}
              onValueChange={setEstadoFilter}
              className="sm:w-52"
            />
            <span className="text-[11px] text-ink-muted sm:ml-auto">{filtrados.length} recursos</span>
          </div>

          {filtrados.length === 0 ? (
            <EmptyState icon={Boxes} title="Sin recursos" description="No hay recursos que coincidan con los filtros." action={<Button variant="secondary" onClick={() => { setSearch(''); setTipoFilter('all'); setEstadoFilter('all') }}>Limpiar filtros</Button>} />
          ) : (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
              {filtrados.map((recurso) => {
                const visual = TIPO_VISUAL[recurso.tipoId] ?? { icon: Package, className: 'bg-sunken text-ink-soft' }
                const Icon = visual.icon
                const asignacion = asignaciones.find((item) => item.recursoId === recurso.id && item.estado === 'Pendiente')
                return (
                  <Card key={recurso.id} className="flex flex-col p-4">
                    <div className="flex items-start gap-3">
                      <span className={`grid size-10 shrink-0 place-items-center rounded-control ${visual.className}`}>
                        <Icon className="size-5" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-bold text-ink">{recurso.nombre}</p>
                        <p className="text-[11px] text-ink-muted">{nombreTipo(recurso.tipoId)}</p>
                      </div>
                      <Badge tone={(ESTADO_RECURSO_TONE[recurso.estado] ?? 'neutral') as Tone} size="sm" dot>
                        {recurso.estado}
                      </Badge>
                    </div>
                    <p className="mt-3 line-clamp-2 text-[11px] leading-relaxed text-ink-muted">{recurso.descripcion}</p>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
                      <div>
                        <p className="text-ink-faint">Costo</p>
                        <p className="tabular font-semibold text-ink">{formatMoney(recurso.costo)}</p>
                      </div>
                      <div>
                        <p className="text-ink-faint">Compra</p>
                        <p className="font-semibold text-ink">{formatDate(recurso.fechaCompra)}</p>
                      </div>
                    </div>
                    {asignacion && (
                      <div className="mt-3 flex items-center gap-2 rounded-control bg-info-soft px-2.5 py-1.5 text-[10px] text-info">
                        <UserRound className="size-3" />
                        Asignado a {nombreUsuario(asignacion.usuarioId)}
                      </div>
                    )}
                    <div className="mt-auto flex items-center justify-end gap-1 pt-3">
                      <Button variant="ghost" size="sm" leftIcon={<Eye className="size-3.5" />} onClick={() => setDetail(recurso)}>Ver</Button>
                      <Button variant="ghost" size="icon" aria-label="Editar recurso" onClick={() => abrirEditar(recurso)}><Pencil className="size-3.5" /></Button>
                      <Button variant="ghost" size="icon" aria-label="Eliminar recurso" onClick={() => setToDelete(recurso)}><Trash2 className="size-3.5 text-danger" /></Button>
                    </div>
                  </Card>
                )
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="tipos">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-[11px] text-ink-muted">{tiposRecurso.length} tipos registrados</p>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={() => { setEditingTipo(null); setTipoOpen(true) }}>
              Nuevo tipo
            </Button>
          </div>
          <Card className="overflow-hidden">
            <div className="hidden overflow-x-auto md:block">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Descripción</th>
                    <th>Recursos</th>
                    <th>Valor</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {tiposRecurso.map((tipo) => {
                    const delTipo = recursos.filter((recurso) => recurso.tipoId === tipo.id)
                    const valor = delTipo.reduce((total, recurso) => total + recurso.costo, 0)
                    return (
                      <tr key={tipo.id}>
                        <td>
                          <span className="flex items-center gap-2 text-sm font-semibold text-ink">
                            <Tags className="size-3.5 text-ink-muted" />
                            {tipo.nombre}
                          </span>
                        </td>
                        <td className="text-xs text-ink-muted">{tipo.descripcion}</td>
                        <td className="tabular text-xs text-ink-soft">{delTipo.length}</td>
                        <td className="tabular text-xs font-semibold text-ink">{formatMoney(valor)}</td>
                        <td>
                          <div className="flex items-center justify-end gap-1">
                            <Button variant="ghost" size="icon" aria-label="Editar tipo" onClick={() => { setEditingTipo(tipo); setTipoOpen(true) }}><Pencil className="size-4" /></Button>
                            <Button variant="ghost" size="icon" aria-label="Eliminar tipo" onClick={() => setToDeleteTipo(tipo)}><Trash2 className="size-4 text-danger" /></Button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
            <div className="divide-y divide-line md:hidden">
              {tiposRecurso.map((tipo) => {
                const delTipo = recursos.filter((recurso) => recurso.tipoId === tipo.id)
                return (
                  <div key={tipo.id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-ink">{tipo.nombre}</p>
                        <p className="text-[11px] text-ink-muted">{tipo.descripcion}</p>
                      </div>
                      <Badge tone="info" size="sm">{delTipo.length} recursos</Badge>
                    </div>
                    <div className="mt-2 flex items-center justify-end gap-1">
                      <Button variant="ghost" size="sm" onClick={() => { setEditingTipo(tipo); setTipoOpen(true) }} leftIcon={<Pencil className="size-3.5" />}>Editar</Button>
                      <Button variant="ghost" size="sm" onClick={() => setToDeleteTipo(tipo)} aria-label="Eliminar tipo"><Trash2 className="size-3.5 text-danger" /></Button>
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="asignaciones">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-[11px] text-ink-muted">{asignaciones.filter((item) => item.estado === 'Pendiente').length} asignaciones activas</p>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={() => setAsignacionOpen(true)}>
              Nueva asignación
            </Button>
          </div>
          {asignaciones.length === 0 ? (
            <EmptyState icon={UserRound} title="Sin asignaciones" description="Aún no hay recursos entregados al equipo." />
          ) : (
            <Card className="overflow-hidden">
              <div className="hidden overflow-x-auto md:block">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Recurso</th>
                      <th>Usuario</th>
                      <th>Asignación</th>
                      <th>Devolución</th>
                      <th>Estado</th>
                      <th className="text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {asignaciones.map((asignacion) => {
                      const recurso = recursos.find((item) => item.id === asignacion.recursoId)
                      return (
                        <tr key={asignacion.id}>
                          <td className="text-sm font-semibold text-ink">{recurso?.nombre ?? `Recurso #${asignacion.recursoId}`}</td>
                          <td>
                            <span className="flex items-center gap-2 text-xs text-ink-soft">
                              <Avatar name={nombreUsuario(asignacion.usuarioId)} size="xs" />
                              {nombreUsuario(asignacion.usuarioId)}
                            </span>
                          </td>
                          <td className="text-xs text-ink-muted">{formatDate(asignacion.fechaAsignacion)}</td>
                          <td className="text-xs text-ink-muted">{formatDate(asignacion.fechaDevolucionEsperada)}</td>
                          <td><Badge tone={ESTADO_ASIGNACION_TONE[asignacion.estado]} size="sm" dot>{asignacion.estado}</Badge></td>
                          <td>
                            <div className="flex justify-end">
                              {asignacion.estado === 'Pendiente' ? (
                                <Button variant="secondary" size="sm" leftIcon={<RotateCcw className="size-3.5" />} onClick={() => setToDevolver(asignacion)}>
                                  Devolver
                                </Button>
                              ) : (
                                <span className="text-[10px] text-ink-faint">{asignacion.fechaDevolucionReal ? formatDate(asignacion.fechaDevolucionReal) : '—'}</span>
                              )}
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <div className="divide-y divide-line md:hidden">
                {asignaciones.map((asignacion) => {
                  const recurso = recursos.find((item) => item.id === asignacion.recursoId)
                  return (
                    <div key={asignacion.id} className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-bold text-ink">{recurso?.nombre ?? `Recurso #${asignacion.recursoId}`}</p>
                          <p className="text-[11px] text-ink-muted">{nombreUsuario(asignacion.usuarioId)} · {formatDate(asignacion.fechaAsignacion)}</p>
                        </div>
                        <Badge tone={ESTADO_ASIGNACION_TONE[asignacion.estado]} size="sm" dot>{asignacion.estado}</Badge>
                      </div>
                      <p className="mt-2 text-[10px] text-ink-muted">Devolución esperada: {formatDate(asignacion.fechaDevolucionEsperada)}</p>
                      {asignacion.estado === 'Pendiente' && (
                        <Button variant="secondary" size="sm" className="mt-2" leftIcon={<RotateCcw className="size-3.5" />} onClick={() => setToDevolver(asignacion)}>
                          Devolver
                        </Button>
                      )}
                    </div>
                  )
                })}
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {recursoOpen && (
        <RecursoFormModal key={`recurso-${editing?.id ?? 'nuevo'}`} open={recursoOpen} onOpenChange={cerrarRecurso} recurso={editing} />
      )}
      {tipoOpen && (
        <TipoFormModal key={`tipo-${editingTipo?.id ?? 'nuevo'}`} open={tipoOpen} onOpenChange={setTipoOpen} tipo={editingTipo} />
      )}
      {asignacionOpen && (
        <AsignacionFormModal open={asignacionOpen} onOpenChange={setAsignacionOpen} />
      )}

      <Drawer
        open={Boolean(detail)}
        onOpenChange={(open) => !open && setDetail(null)}
        title={detail?.nombre ?? 'Recurso'}
        description={detail ? nombreTipo(detail.tipoId) : undefined}
        footer={
          detail && (
            <>
              <Button variant="ghost" onClick={() => setDetail(null)}>Cerrar</Button>
              <Button onClick={() => abrirEditar(detail)} leftIcon={<Pencil className="size-4" />}>Editar</Button>
            </>
          )
        }
      >
        {detail && (() => {
          const visual = TIPO_VISUAL[detail.tipoId] ?? { icon: Package, className: 'bg-sunken text-ink-soft' }
          const Icon = visual.icon
          const historial = asignaciones.filter((asignacion) => asignacion.recursoId === detail.id)
          return (
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <span className={`grid size-14 place-items-center rounded-card ${visual.className}`}>
                  <Icon className="size-6" />
                </span>
                <div>
                  <p className="text-lg font-bold text-ink">{detail.nombre}</p>
                  <Badge tone={(ESTADO_RECURSO_TONE[detail.estado] ?? 'neutral') as Tone} size="sm" dot>{detail.estado}</Badge>
                </div>
              </div>
              <p className="text-sm leading-relaxed text-ink-muted">{detail.descripcion}</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-control border border-line bg-sunken/35 p-3">
                  <p className="text-[10px] uppercase tracking-wide text-ink-muted">Costo</p>
                  <p className="tabular mt-1 text-sm font-bold text-ink">{formatMoney(detail.costo)}</p>
                </div>
                <div className="rounded-control border border-line bg-sunken/35 p-3">
                  <p className="text-[10px] uppercase tracking-wide text-ink-muted">Fecha de compra</p>
                  <p className="mt-1 text-sm font-bold text-ink">{formatDate(detail.fechaCompra)}</p>
                </div>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Historial de asignaciones</p>
                {historial.length === 0 ? (
                  <p className="mt-2 text-xs text-ink-muted">Sin asignaciones registradas.</p>
                ) : (
                  <div className="mt-2 space-y-1.5">
                    {historial.map((asignacion) => (
                      <div key={asignacion.id} className="flex items-center justify-between rounded-control border border-line px-3 py-2">
                        <div>
                          <p className="text-xs font-semibold text-ink">{nombreUsuario(asignacion.usuarioId)}</p>
                          <p className="text-[10px] text-ink-muted">{formatDate(asignacion.fechaAsignacion)} · {asignacion.notas || 'Sin notas'}</p>
                        </div>
                        <Badge tone={ESTADO_ASIGNACION_TONE[asignacion.estado]} size="sm">{asignacion.estado}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })()}
      </Drawer>

      <ConfirmDialog open={Boolean(toDelete)} onOpenChange={(open) => !open && setToDelete(null)} title="Eliminar recurso" description={toDelete ? `Se eliminará "${toDelete.nombre}" del inventario.` : ''} confirmLabel="Eliminar" onConfirm={confirmarEliminar} />
      <ConfirmDialog open={Boolean(toDeleteTipo)} onOpenChange={(open) => !open && setToDeleteTipo(null)} title="Eliminar tipo" description={toDeleteTipo ? `Se eliminará el tipo "${toDeleteTipo.nombre}".` : ''} confirmLabel="Eliminar" onConfirm={confirmarEliminarTipo} />
      <ConfirmDialog open={Boolean(toDevolver)} onOpenChange={(open) => !open && setToDevolver(null)} title="Devolver recurso" description={toDevolver ? `Se registrará la devolución del recurso al inventario.` : ''} confirmLabel="Devolver" onConfirm={confirmarDevolucion} />
    </div>
  )
}

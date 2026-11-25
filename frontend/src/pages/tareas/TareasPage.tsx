import { zodResolver } from '@hookform/resolvers/zod'
import {
  CalendarDays,
  Check,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  Clock,
  Pencil,
  Play,
  Plus,
  RotateCcw,
  Trash2,
  UserPlus,
} from 'lucide-react'
import { LayoutGroup, motion } from 'motion/react'
import { useMemo, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Avatar } from '@/components/ui/Avatar'
import { Badge, type Tone } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Drawer } from '@/components/ui/Drawer'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input, Textarea } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SegmentedControl } from '@/components/ui/SegmentedControl'
import { Select } from '@/components/ui/Select'
import { useData } from '@/hooks/useData'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { useSession } from '@/hooks/useSession'
import { PRIORIDAD_OPTIONS, PRIORIDAD_TONE } from '@/lib/constants'
import { formatDate } from '@/lib/format'
import { tareaSchema, type TareaForm } from '@/lib/schemas'
import type { EstadoTarea, Tarea } from '@/types'

const ESTADOS: { estado: EstadoTarea; label: string; tone: Tone; icon: typeof Clock }[] = [
  { estado: 'Pendiente', label: 'Pendiente', tone: 'time', icon: Clock },
  { estado: 'En progreso', label: 'En progreso', tone: 'info', icon: Play },
  { estado: 'Completada', label: 'Completada', tone: 'live', icon: CheckCircle2 },
]

function TareaFormModal({
  open,
  onOpenChange,
  tarea,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  tarea: Tarea | null
}) {
  const { usuarios, saveTarea } = useData()
  const form = useForm<TareaForm>({
    resolver: zodResolver(tareaSchema),
    defaultValues: {
      nombre: tarea?.nombre ?? '',
      instruccion: tarea?.instruccion ?? '',
      asignadoId: tarea ? String(tarea.asignadoId) : '',
      fecha: tarea?.fecha ?? '2026-07-10',
      prioridad: tarea?.prioridad ?? 'Media',
    },
  })

  const onSubmit = (values: TareaForm) => {
    saveTarea(
      {
        nombre: values.nombre,
        instruccion: values.instruccion,
        asignadoId: Number(values.asignadoId),
        fecha: values.fecha,
        prioridad: values.prioridad,
      },
      tarea?.id,
    )
    toast.success(tarea ? 'Tarea actualizada' : 'Tarea registrada')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={tarea ? 'Editar tarea' : 'Nueva tarea'}
      description="Instrucción y responsable de la actividad."
      icon={ClipboardCheck}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {tarea ? 'Guardar cambios' : 'Registrar tarea'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
        <Input label="Nombre de la tarea" placeholder="Ej: Verificar equipo de transmisión" error={form.formState.errors.nombre?.message} className="sm:col-span-2" {...form.register('nombre')} />
        <Textarea label="Instrucción" placeholder="Describe qué debe hacer el responsable..." error={form.formState.errors.instruccion?.message} className="sm:col-span-2" {...form.register('instruccion')} />
        <Controller
          control={form.control}
          name="asignadoId"
          render={({ field }) => (
            <Select
              label="Responsable"
              placeholder="Selecciona un responsable"
              options={usuarios.filter((usuario) => usuario.activo).map((usuario) => ({ value: String(usuario.id), label: `${usuario.nombre} · ${usuario.departamento}` }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.asignadoId?.message}
            />
          )}
        />
        <Input label="Fecha" type="date" error={form.formState.errors.fecha?.message} {...form.register('fecha')} />
        <Controller
          control={form.control}
          name="prioridad"
          render={({ field }) => (
            <Select
              label="Prioridad"
              options={PRIORIDAD_OPTIONS}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.prioridad?.message}
              className="sm:col-span-2"
            />
          )}
        />
      </form>
    </Modal>
  )
}

function AsignarTareaModal({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const { tareas, usuarios, saveTarea } = useData()
  const [tareaId, setTareaId] = useState('')
  const [usuarioId, setUsuarioId] = useState('')
  const [fecha, setFecha] = useState('2026-07-10')

  const guardar = () => {
    const tarea = tareas.find((item) => String(item.id) === tareaId)
    if (!tarea || !usuarioId) {
      toast.error('Selecciona una tarea y un responsable')
      return
    }
    saveTarea(
      {
        nombre: tarea.nombre,
        instruccion: tarea.instruccion,
        asignadoId: Number(usuarioId),
        fecha,
        prioridad: tarea.prioridad,
      },
      tarea.id,
    )
    toast.success('Tarea asignada')
    setTareaId('')
    setUsuarioId('')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Asignar tarea"
      description="Reasigna una actividad existente a otro miembro del equipo."
      icon={UserPlus}
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={guardar}>Asignar tarea</Button>
        </>
      }
    >
      <div className="space-y-4">
        <Select
          label="Tarea"
          placeholder="Selecciona una tarea"
          options={tareas.map((tarea) => ({ value: String(tarea.id), label: tarea.nombre }))}
          value={tareaId}
          onValueChange={setTareaId}
        />
        <Select
          label="Responsable"
          placeholder="Selecciona un usuario"
          options={usuarios.filter((usuario) => usuario.activo).map((usuario) => ({ value: String(usuario.id), label: `${usuario.nombre} · ${usuario.departamento}` }))}
          value={usuarioId}
          onValueChange={setUsuarioId}
        />
        <Input label="Fecha" type="date" value={fecha} onChange={(event) => setFecha(event.target.value)} />
      </div>
    </Modal>
  )
}

function TareaCard({
  tarea,
  usuario,
  onOpen,
  onEstado,
  onEdit,
  onDelete,
}: {
  tarea: Tarea
  usuario?: string
  onOpen: () => void
  onEstado: (estado: EstadoTarea) => void
  onEdit: () => void
  onDelete: () => void
}) {
  return (
    <motion.div
      layout
      layoutId={`tarea-${tarea.id}`}
      transition={{ duration: 0.25, ease: [0.23, 1, 0.32, 1] }}
      className="rounded-control border border-line bg-surface p-3 shadow-card"
    >
      <div className="flex items-start justify-between gap-2">
        <Badge tone={(PRIORIDAD_TONE[tarea.prioridad] ?? 'neutral') as Tone} size="sm">
          {tarea.prioridad}
        </Badge>
        <div className="flex items-center gap-0.5">
          <Button variant="ghost" size="icon" className="size-7" aria-label="Editar tarea" onClick={onEdit}>
            <Pencil className="size-3" />
          </Button>
          <Button variant="ghost" size="icon" className="size-7" aria-label="Eliminar tarea" onClick={onDelete}>
            <Trash2 className="size-3 text-danger" />
          </Button>
        </div>
      </div>
      <button type="button" onClick={onOpen} className="mt-2 block w-full text-left">
        <p className="text-sm font-bold leading-snug text-ink">{tarea.nombre}</p>
        <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-ink-muted">{tarea.instruccion}</p>
      </button>
      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="flex min-w-0 items-center gap-1.5">
          <Avatar name={usuario ?? 'Sin asignar'} size="xs" />
          <span className="truncate text-[10px] text-ink-muted">{usuario ?? 'Sin asignar'}</span>
        </span>
        <span className="flex items-center gap-1 text-[10px] text-ink-muted">
          <CalendarDays className="size-3" />
          {formatDate(tarea.fecha)}
        </span>
      </div>
      <div className="mt-3 flex items-center justify-end">
        {tarea.estado === 'Pendiente' && (
          <Button variant="secondary" size="sm" leftIcon={<Play className="size-3" />} onClick={() => onEstado('En progreso')}>
            Iniciar
          </Button>
        )}
        {tarea.estado === 'En progreso' && (
          <Button variant="live" size="sm" leftIcon={<Check className="size-3" />} onClick={() => onEstado('Completada')}>
            Completar
          </Button>
        )}
        {tarea.estado === 'Completada' && (
          <Button variant="ghost" size="sm" leftIcon={<RotateCcw className="size-3" />} onClick={() => onEstado('Pendiente')}>
            Reabrir
          </Button>
        )}
      </div>
    </motion.div>
  )
}

export function TareasPage() {
  const { tareas, usuarios, deleteTarea, setTareaEstado } = useData()
  const { user } = useSession()
  const isDesktop = useMediaQuery('(min-width: 1024px)')
  const [searchParams, setSearchParams] = useSearchParams()
  const [vista, setVista] = useState('mias')
  const [mobileEstado, setMobileEstado] = useState<EstadoTarea>('Pendiente')
  const [formOpen, setFormOpen] = useState(() => searchParams.get('nueva') === '1')
  const [editing, setEditing] = useState<Tarea | null>(null)
  const [assignOpen, setAssignOpen] = useState(false)
  const [selected, setSelected] = useState<Tarea | null>(null)
  const [toDelete, setToDelete] = useState<Tarea | null>(null)

  const cerrarFormulario = (open: boolean) => {
    setFormOpen(open)
    if (!open && searchParams.get('nueva')) setSearchParams({}, { replace: true })
  }

  const visibles = useMemo(
    () => (vista === 'mias' ? tareas.filter((tarea) => tarea.asignadoId === user?.id) : tareas),
    [tareas, vista, user],
  )

  const nombreUsuario = (id: number) => usuarios.find((usuario) => usuario.id === id)?.nombre ?? 'Sin asignar'
  const porEstado = (estado: EstadoTarea) => visibles.filter((tarea) => tarea.estado === estado)
  const completadas = visibles.filter((tarea) => tarea.estado === 'Completada').length

  const cambiarEstado = (tarea: Tarea, estado: EstadoTarea) => {
    setTareaEstado(tarea.id, estado)
    if (estado === 'Completada') {
      toast.success('Tarea completada', { description: 'Se notificó al creador de la tarea.' })
    } else {
      toast.success(estado === 'En progreso' ? 'Tarea iniciada' : 'Tarea reabierta')
    }
  }

  const confirmarEliminar = () => {
    if (!toDelete) return
    deleteTarea(toDelete.id)
    toast.success('Tarea eliminada')
    setToDelete(null)
  }

  const abrirEditar = (tarea: Tarea) => {
    setSelected(null)
    setEditing(tarea)
    setFormOpen(true)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Módulo de asignaciones"
        title="Tareas"
        description="Asignaciones y avance de la jornada en el palco."
        actions={
          <>
            <Button variant="secondary" size="sm" leftIcon={<UserPlus className="size-3.5" />} onClick={() => setAssignOpen(true)}>
              Asignar tarea
            </Button>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={() => { setEditing(null); setFormOpen(true) }}>
              Nueva tarea
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          { label: 'Tareas', value: String(visibles.length), hint: vista === 'mias' ? 'Asignadas a ti' : 'En el sistema', tone: 'info', icon: ClipboardList },
          { label: 'Pendientes', value: String(porEstado('Pendiente').length), hint: 'Sin iniciar', tone: 'time', icon: Clock },
          { label: 'En progreso', value: String(porEstado('En progreso').length), hint: 'En ejecución', tone: 'brand', icon: Play },
          { label: 'Completadas', value: String(completadas), hint: 'Cerradas hoy', tone: 'live', icon: CheckCircle2 },
        ]}
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <SegmentedControl
          value={vista}
          onValueChange={setVista}
          ariaLabel="Vista de tareas"
          options={[
            { value: 'mias', label: 'Mis tareas' },
            { value: 'todas', label: 'Todas' },
          ]}
        />
        <SegmentedControl
          value={mobileEstado}
          onValueChange={(value) => setMobileEstado(value as EstadoTarea)}
          ariaLabel="Filtrar por estado"
          className="lg:hidden"
          options={ESTADOS.map((estado) => ({ value: estado.estado, label: estado.label }))}
        />
      </div>

      {isDesktop && (
        <LayoutGroup>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          {ESTADOS.map((columna) => {
            const items = porEstado(columna.estado)
            const Icon = columna.icon
            return (
              <div key={columna.estado} className="rounded-card border border-line bg-surface/45 p-3">
                <div className="mb-3 flex items-center justify-between px-1">
                  <div className="flex items-center gap-2">
                    <span className={`size-1.5 rounded-full ${
                      columna.tone === 'time' ? 'bg-time' : columna.tone === 'info' ? 'bg-info' : 'bg-live'
                    }`} />
                    <p className="text-xs font-bold uppercase tracking-[0.1em] text-ink-muted">{columna.label}</p>
                  </div>
                  <span className="grid size-5 place-items-center rounded-full bg-sunken text-[10px] font-bold text-ink-muted">
                    {items.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {items.length === 0 ? (
                    <div className="flex flex-col items-center justify-center rounded-control border border-dashed border-line px-3 py-10 text-center">
                      <Icon className="size-5 text-ink-faint" />
                      <p className="mt-2 text-[11px] text-ink-muted">Sin tareas en este estado</p>
                    </div>
                  ) : (
                    items.map((tarea) => (
                      <TareaCard
                        key={tarea.id}
                        tarea={tarea}
                        usuario={nombreUsuario(tarea.asignadoId)}
                        onOpen={() => setSelected(tarea)}
                        onEstado={(estado) => cambiarEstado(tarea, estado)}
                        onEdit={() => abrirEditar(tarea)}
                        onDelete={() => setToDelete(tarea)}
                      />
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </LayoutGroup>
      )}

      {!isDesktop && (
      <div className="space-y-2">
        {porEstado(mobileEstado).length === 0 ? (
          <EmptyState icon={ClipboardCheck} title="Sin tareas" description="No hay tareas en este estado para la vista seleccionada." />
        ) : (
          porEstado(mobileEstado).map((tarea) => (
            <TareaCard
              key={tarea.id}
              tarea={tarea}
              usuario={nombreUsuario(tarea.asignadoId)}
              onOpen={() => setSelected(tarea)}
              onEstado={(estado) => cambiarEstado(tarea, estado)}
              onEdit={() => abrirEditar(tarea)}
              onDelete={() => setToDelete(tarea)}
            />
          ))
        )}
      </div>
      )}

      {formOpen && (
        <TareaFormModal key={editing?.id ?? 'nuevo'} open={formOpen} onOpenChange={cerrarFormulario} tarea={editing} />
      )}
      {assignOpen && (
        <AsignarTareaModal open={assignOpen} onOpenChange={setAssignOpen} />
      )}

      <Drawer
        open={Boolean(selected)}
        onOpenChange={(open) => !open && setSelected(null)}
        title={selected?.nombre ?? 'Tarea'}
        description={selected ? `Creada por ${nombreUsuario(selected.creadorId)}` : undefined}
        footer={
          selected && (
            <>
              <Button variant="ghost" onClick={() => setSelected(null)}>Cerrar</Button>
              <Button variant="secondary" onClick={() => abrirEditar(selected)} leftIcon={<Pencil className="size-4" />}>Editar</Button>
            </>
          )
        }
      >
        {selected && (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={selected.estado === 'Completada' ? 'live' : selected.estado === 'En progreso' ? 'info' : 'time'} dot>
                {selected.estado}
              </Badge>
              <Badge tone={(PRIORIDAD_TONE[selected.prioridad] ?? 'neutral') as Tone}>
                Prioridad {selected.prioridad}
              </Badge>
            </div>
            <p className="text-sm leading-relaxed text-ink-soft">{selected.instruccion}</p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Responsable</p>
                <div className="mt-1.5 flex items-center gap-2">
                  <Avatar name={nombreUsuario(selected.asignadoId)} size="sm" />
                  <span className="text-sm font-semibold text-ink">{nombreUsuario(selected.asignadoId)}</span>
                </div>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Fecha</p>
                <p className="mt-1.5 text-sm font-semibold text-ink">{formatDate(selected.fecha)}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {selected.estado === 'Pendiente' && (
                <Button variant="secondary" onClick={() => { cambiarEstado(selected, 'En progreso'); setSelected(null) }} leftIcon={<Play className="size-4" />}>
                  Iniciar tarea
                </Button>
              )}
              {selected.estado === 'En progreso' && (
                <Button variant="live" onClick={() => { cambiarEstado(selected, 'Completada'); setSelected(null) }} leftIcon={<Check className="size-4" />}>
                  Completar tarea
                </Button>
              )}
              {selected.estado === 'Completada' && (
                <Button variant="ghost" onClick={() => { cambiarEstado(selected, 'Pendiente'); setSelected(null) }} leftIcon={<RotateCcw className="size-4" />}>
                  Reabrir tarea
                </Button>
              )}
            </div>
          </div>
        )}
      </Drawer>

      <ConfirmDialog
        open={Boolean(toDelete)}
        onOpenChange={(open) => !open && setToDelete(null)}
        title="Eliminar tarea"
        description={toDelete ? `Se eliminará "${toDelete.nombre}" del tablero.` : ''}
        confirmLabel="Eliminar"
        onConfirm={confirmarEliminar}
      />
    </div>
  )
}

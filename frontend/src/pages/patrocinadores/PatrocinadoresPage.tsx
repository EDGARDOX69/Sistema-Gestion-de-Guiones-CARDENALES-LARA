import { zodResolver } from '@hookform/resolvers/zod'
import {
  Building2,
  CalendarClock,
  Download,
  Eye,
  FileText,
  Filter,
  Handshake,
  Mail,
  Pencil,
  Phone,
  Plus,
  Trash2,
  UserRound,
  Wallet,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Drawer } from '@/components/ui/Drawer'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Progress } from '@/components/ui/Progress'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SearchInput } from '@/components/ui/SearchInput'
import { Select } from '@/components/ui/Select'
import { useData } from '@/hooks/useData'
import {
  ESTADO_CONTRATO_TONE,
  TIPO_CONTRATO_LABEL,
  TIPO_CONTRATO_OPTIONS,
} from '@/lib/constants'
import { daysUntil, formatDate, formatMoney, percent } from '@/lib/format'
import { patrocinadorSchema, type PatrocinadorForm } from '@/lib/schemas'
import {
  contratoDePatrocinador,
  pagosDeContrato,
  totalContratado,
  totalPagadoPorContrato,
} from '@/lib/selectors'
import type { Patrocinador } from '@/types'

const TIPO_TONE = {
  1: 'brand',
  2: 'info',
  3: 'time',
} as const

const ESTADO_OPTIONS = [
  { value: 'activos', label: 'Activos' },
  { value: 'todos', label: 'Todos' },
]

function PatrocinadorFormModal({
  open,
  onOpenChange,
  patrocinador,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  patrocinador: Patrocinador | null
}) {
  const { usuarios, savePatrocinador } = useData()
  const form = useForm<PatrocinadorForm>({
    resolver: zodResolver(patrocinadorSchema),
    defaultValues: {
      nombre: patrocinador?.nombre ?? '',
      rif: patrocinador?.rif ?? '',
      tipoContrato: patrocinador ? String(patrocinador.tipoContrato) : '',
      contacto: patrocinador?.contacto ?? '',
      telefono: patrocinador?.telefono ?? '',
      email: patrocinador?.email ?? '',
      encargadoId: patrocinador ? String(patrocinador.encargadoId) : '',
    },
  })

  const encargados = usuarios
    .filter((usuario) => usuario.rol === 'Administrador' || usuario.rol === 'Superadmin')
    .map((usuario) => ({ value: String(usuario.id), label: `${usuario.nombre} · ${usuario.rol}` }))

  const onSubmit = (values: PatrocinadorForm) => {
    savePatrocinador(
      {
        nombre: values.nombre,
        rif: values.rif,
        tipoContrato: Number(values.tipoContrato),
        contacto: values.contacto,
        telefono: values.telefono,
        email: values.email,
        encargadoId: Number(values.encargadoId),
      },
      patrocinador?.id,
    )
    toast.success(patrocinador ? 'Patrocinante actualizado' : 'Patrocinante registrado')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={patrocinador ? 'Editar patrocinante' : 'Nuevo patrocinante'}
      description="Datos comerciales y de contacto de la marca."
      icon={Handshake}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {patrocinador ? 'Guardar cambios' : 'Registrar patrocinante'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
        <Input
          label="Nombre de la empresa"
          placeholder="Ej: Maltin Polar"
          error={form.formState.errors.nombre?.message}
          className="sm:col-span-2"
          {...form.register('nombre')}
        />
        <Input
          label="RIF"
          placeholder="J-00000000-0"
          error={form.formState.errors.rif?.message}
          {...form.register('rif')}
        />
        <Controller
          control={form.control}
          name="tipoContrato"
          render={({ field }) => (
            <Select
              label="Tipo de contrato"
              placeholder="Selecciona un tipo"
              options={TIPO_CONTRATO_OPTIONS}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.tipoContrato?.message}
            />
          )}
        />
        <Input
          label="Nombre del contacto"
          placeholder="Persona de contacto"
          error={form.formState.errors.contacto?.message}
          {...form.register('contacto')}
        />
        <Input
          label="Teléfono"
          placeholder="0212-000-0000"
          error={form.formState.errors.telefono?.message}
          {...form.register('telefono')}
        />
        <Input
          label="Correo electrónico"
          type="email"
          placeholder="contacto@empresa.com"
          error={form.formState.errors.email?.message}
          {...form.register('email')}
        />
        <Controller
          control={form.control}
          name="encargadoId"
          render={({ field }) => (
            <Select
              label="Encargado"
              placeholder="Selecciona un encargado"
              options={encargados}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.encargadoId?.message}
            />
          )}
        />
      </form>
    </Modal>
  )
}

function Filtros({
  search,
  onSearch,
  tipo,
  onTipo,
  encargado,
  onEncargado,
  estado,
  onEstado,
  onClear,
  encargados,
}: {
  search: string
  onSearch: (value: string) => void
  tipo: string
  onTipo: (value: string) => void
  encargado: string
  onEncargado: (value: string) => void
  estado: string
  onEstado: (value: string) => void
  onClear: () => void
  encargados: { value: string; label: string }[]
}) {
  return (
    <div className="space-y-4">
      <SearchInput value={search} onChange={onSearch} placeholder="Buscar marca, RIF o contacto" />
      <Select
        label="Tipo de contrato"
        options={[{ value: 'all', label: 'Todos los tipos' }, ...TIPO_CONTRATO_OPTIONS]}
        value={tipo}
        onValueChange={onTipo}
      />
      <Select
        label="Encargado"
        options={[{ value: 'all', label: 'Todos los encargados' }, ...encargados]}
        value={encargado}
        onValueChange={onEncargado}
      />
      <Select label="Estado" options={ESTADO_OPTIONS} value={estado} onValueChange={onEstado} />
      <Button variant="secondary" className="w-full" onClick={onClear} leftIcon={<Filter className="size-4" />}>
        Limpiar filtros
      </Button>
    </div>
  )
}

export function PatrocinadoresPage() {
  const { patrocinadores, contratos, pagos, usuarios, deletePatrocinador } = useData()
  const [searchParams, setSearchParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const [tipo, setTipo] = useState('all')
  const [encargado, setEncargado] = useState('all')
  const [estado, setEstado] = useState('activos')
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [modalOpen, setModalOpen] = useState(() => searchParams.get('nuevo') === '1')
  const [editing, setEditing] = useState<Patrocinador | null>(null)
  const [selected, setSelected] = useState<Patrocinador | null>(null)
  const [toDelete, setToDelete] = useState<Patrocinador | null>(null)

  const cerrarModal = (open: boolean) => {
    setModalOpen(open)
    if (!open && searchParams.get('nuevo')) setSearchParams({}, { replace: true })
  }

  const encargados = usuarios
    .filter((usuario) => usuario.rol === 'Administrador' || usuario.rol === 'Superadmin')
    .map((usuario) => ({ value: String(usuario.id), label: usuario.nombre }))

  const filtrados = useMemo(() => {
    const term = search.trim().toLowerCase()
    return patrocinadores.filter((patrocinador) => {
      const coincideTexto =
        !term ||
        patrocinador.nombre.toLowerCase().includes(term) ||
        patrocinador.rif.toLowerCase().includes(term) ||
        patrocinador.contacto.toLowerCase().includes(term)
      const coincideTipo = tipo === 'all' || String(patrocinador.tipoContrato) === tipo
      const coincideEncargado = encargado === 'all' || String(patrocinador.encargadoId) === encargado
      const coincideEstado = estado === 'todos' || patrocinador.estado
      return coincideTexto && coincideTipo && coincideEncargado && coincideEstado
    })
  }, [patrocinadores, search, tipo, encargado, estado])

  const contratado = totalContratado(contratos)
  const activos = contratos.filter((contrato) => contrato.estado === 'Vigente').length
  const porVencer = contratos.filter((contrato) => {
    const dias = daysUntil(contrato.fin)
    return dias >= 0 && dias <= 45
  }).length

  const limpiar = () => {
    setSearch('')
    setTipo('all')
    setEncargado('all')
    setEstado('activos')
  }

  const abrirNuevo = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const abrirEditar = (patrocinador: Patrocinador) => {
    setSelected(null)
    setEditing(patrocinador)
    setModalOpen(true)
  }

  const confirmarEliminar = () => {
    if (!toDelete) return
    deletePatrocinador(toDelete.id)
    toast.success('Patrocinante eliminado')
    setToDelete(null)
  }

  const nombreEncargado = (id: number) => usuarios.find((usuario) => usuario.id === id)?.nombre ?? 'Sin asignar'

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Módulo comercial"
        title="Patrocinantes"
        description="Marcas, contratos y contacto comercial de la temporada."
        actions={
          <>
            <Button variant="secondary" size="sm" leftIcon={<Download className="size-3.5" />} onClick={() => toast.success('Directorio listo para exportar')}>
              Exportar
            </Button>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={abrirNuevo}>
              Nuevo patrocinante
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          { label: 'Marcas activas', value: String(patrocinadores.length), hint: 'Registradas en el sistema', tone: 'brand', icon: Handshake },
          { label: 'Contratos vigentes', value: String(activos), hint: `${contratos.length} contratos en total`, tone: 'live', icon: FileText },
          { label: 'Contratado', value: formatMoney(contratado), hint: 'Monto de la temporada', tone: 'info', icon: Wallet },
          { label: 'Por vencer', value: String(porVencer), hint: 'Próximos 45 días', tone: 'time', icon: CalendarClock },
        ]}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[260px_1fr]">
        <Card className="hidden h-fit p-4 lg:block">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm font-bold text-ink">Filtros</p>
            <Filter className="size-4 text-ink-faint" />
          </div>
          <Filtros
            search={search}
            onSearch={setSearch}
            tipo={tipo}
            onTipo={setTipo}
            encargado={encargado}
            onEncargado={setEncargado}
            estado={estado}
            onEstado={setEstado}
            onClear={limpiar}
            encargados={encargados}
          />
        </Card>

        <Card className="overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-line p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-bold text-ink">Directorio comercial</p>
              <p className="text-[11px] text-ink-muted">
                {filtrados.length} de {patrocinadores.length} marcas
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="secondary" size="sm" className="lg:hidden" onClick={() => setFiltersOpen(true)} leftIcon={<Filter className="size-3.5" />}>
                Filtros
              </Button>
            </div>
          </div>

          {filtrados.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon={Handshake}
                title="Sin patrocinantes"
                description="No hay marcas que coincidan con los filtros actuales."
                action={<Button variant="secondary" onClick={limpiar}>Limpiar filtros</Button>}
              />
            </div>
          ) : (
            <>
              <div className="hidden overflow-x-auto md:block">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Patrocinante</th>
                      <th>Tipo</th>
                      <th>Contacto</th>
                      <th>Contrato</th>
                      <th>Estado</th>
                      <th className="text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtrados.map((patrocinador) => {
                      const contrato = contratoDePatrocinador(contratos, patrocinador.id)
                      const pagadoContrato = contrato ? totalPagadoPorContrato(pagos, contrato.id) : 0
                      const pct = contrato ? percent(pagadoContrato, contrato.montoTotal) : 0
                      return (
                        <tr key={patrocinador.id}>
                          <td>
                            <div className="flex items-center gap-2.5">
                              <Avatar name={patrocinador.nombre} size="sm" />
                              <div className="min-w-0">
                                <p className="truncate text-sm font-semibold text-ink">{patrocinador.nombre}</p>
                                <p className="truncate text-[10px] text-ink-muted">
                                  <span className="font-mono text-ink-faint">{patrocinador.rif}</span>
                                  {' · '}
                                  {patrocinador.email || 'Sin correo'}
                                </p>
                              </div>
                            </div>
                          </td>
                          <td>
                            <Badge tone={TIPO_TONE[patrocinador.tipoContrato]} size="sm">
                              {TIPO_CONTRATO_LABEL[patrocinador.tipoContrato]}
                            </Badge>
                          </td>
                          <td className="max-w-[160px]">
                            <p className="truncate text-xs font-medium text-ink-soft">{patrocinador.contacto}</p>
                            <p className="truncate text-[10px] text-ink-muted">{nombreEncargado(patrocinador.encargadoId)}</p>
                          </td>
                          <td className="min-w-40">
                            {contrato ? (
                              <div>
                                <div className="flex items-center justify-between text-[10px] text-ink-muted">
                                  <span>{formatMoney(pagadoContrato)}</span>
                                  <span>{Math.round(pct)}%</span>
                                </div>
                                <Progress value={pct} tone="live" size="sm" className="mt-1.5" />
                              </div>
                            ) : (
                              <span className="text-xs text-ink-muted">Sin contrato</span>
                            )}
                          </td>
                          <td>
                            <Badge tone={contrato ? ESTADO_CONTRATO_TONE[contrato.estado] as 'live' | 'danger' : 'neutral'} size="sm" dot>
                              {contrato?.estado ?? 'Sin contrato'}
                            </Badge>
                          </td>
                          <td>
                            <div className="flex items-center justify-end gap-1">
                              <Button variant="ghost" size="icon" aria-label="Ver detalle" onClick={() => setSelected(patrocinador)}>
                                <Eye className="size-4" />
                              </Button>
                              <Button variant="ghost" size="icon" aria-label="Editar" onClick={() => abrirEditar(patrocinador)}>
                                <Pencil className="size-4" />
                              </Button>
                              <Button variant="ghost" size="icon" aria-label="Eliminar" onClick={() => setToDelete(patrocinador)}>
                                <Trash2 className="size-4 text-danger" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <div className="divide-y divide-line md:hidden">
                {filtrados.map((patrocinador) => {
                  const contrato = contratoDePatrocinador(contratos, patrocinador.id)
                  const pagadoContrato = contrato ? totalPagadoPorContrato(pagos, contrato.id) : 0
                  const pct = contrato ? percent(pagadoContrato, contrato.montoTotal) : 0
                  return (
                    <div key={patrocinador.id} className="p-4">
                      <div className="flex items-start gap-3">
                        <Avatar name={patrocinador.nombre} size="md" />
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-bold text-ink">{patrocinador.nombre}</p>
                          <p className="text-[11px] text-ink-muted">{patrocinador.rif} · {patrocinador.contacto}</p>
                          <div className="mt-2 flex flex-wrap items-center gap-1.5">
                            <Badge tone={TIPO_TONE[patrocinador.tipoContrato]} size="sm">
                              {TIPO_CONTRATO_LABEL[patrocinador.tipoContrato]}
                            </Badge>
                            <Badge tone={contrato ? ESTADO_CONTRATO_TONE[contrato.estado] as 'live' | 'danger' : 'neutral'} size="sm">
                              {contrato?.estado ?? 'Sin contrato'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      {contrato && (
                        <div className="mt-3">
                          <div className="flex items-center justify-between text-[10px] text-ink-muted">
                            <span>{formatMoney(pagadoContrato)} de {formatMoney(contrato.montoTotal)}</span>
                            <span>{Math.round(pct)}%</span>
                          </div>
                          <Progress value={pct} tone="live" size="sm" className="mt-1.5" />
                        </div>
                      )}
                      <div className="mt-3 flex items-center justify-end gap-1">
                        <Button variant="ghost" size="sm" onClick={() => setSelected(patrocinador)} leftIcon={<Eye className="size-3.5" />}>
                          Ver
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => abrirEditar(patrocinador)} leftIcon={<Pencil className="size-3.5" />}>
                          Editar
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setToDelete(patrocinador)} aria-label="Eliminar">
                          <Trash2 className="size-3.5 text-danger" />
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </Card>
      </div>

      {modalOpen && (
        <PatrocinadorFormModal
          key={editing?.id ?? 'nuevo'}
          open={modalOpen}
          onOpenChange={cerrarModal}
          patrocinador={editing}
        />
      )}

      <Modal
        open={filtersOpen}
        onOpenChange={setFiltersOpen}
        title="Filtros"
        description="Acota el directorio comercial."
        icon={Filter}
        footer={
          <>
            <Button variant="ghost" onClick={limpiar}>Limpiar</Button>
            <Button onClick={() => setFiltersOpen(false)}>Aplicar</Button>
          </>
        }
      >
        <Filtros
          search={search}
          onSearch={setSearch}
          tipo={tipo}
          onTipo={setTipo}
          encargado={encargado}
          onEncargado={setEncargado}
          estado={estado}
          onEstado={setEstado}
          onClear={limpiar}
          encargados={encargados}
        />
      </Modal>

      <Drawer
        open={Boolean(selected)}
        onOpenChange={(open) => !open && setSelected(null)}
        title={selected?.nombre ?? 'Patrocinante'}
        description={selected ? `${selected.rif} · ${TIPO_CONTRATO_LABEL[selected.tipoContrato]}` : undefined}
        width="lg"
        footer={
          selected && (
            <>
              <Button variant="ghost" onClick={() => setSelected(null)}>Cerrar</Button>
              <Button onClick={() => abrirEditar(selected)} leftIcon={<Pencil className="size-4" />}>Editar</Button>
            </>
          )
        }
      >
        {selected && (
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <Avatar name={selected.nombre} size="lg" />
              <div>
                <p className="text-lg font-bold text-ink">{selected.nombre}</p>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  <Badge tone={TIPO_TONE[selected.tipoContrato]} size="sm">{TIPO_CONTRATO_LABEL[selected.tipoContrato]}</Badge>
                  <Badge tone={selected.estado ? 'live' : 'neutral'} size="sm" dot>{selected.estado ? 'Activo' : 'Inactivo'}</Badge>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><UserRound className="size-3" /> Contacto</p>
                <p className="mt-1 text-sm font-semibold text-ink">{selected.contacto}</p>
                <p className="mt-0.5 text-[11px] text-ink-muted">Encargado: {nombreEncargado(selected.encargadoId)}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Building2 className="size-3" /> RIF</p>
                <p className="mt-1 font-mono text-sm font-semibold text-ink">{selected.rif}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Phone className="size-3" /> Teléfono</p>
                <p className="mt-1 text-sm font-semibold text-ink">{selected.telefono || 'No registrado'}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Mail className="size-3" /> Correo</p>
                <p className="mt-1 truncate text-sm font-semibold text-ink">{selected.email || 'No registrado'}</p>
              </div>
            </div>

            {(() => {
              const contrato = contratoDePatrocinador(contratos, selected.id)
              if (!contrato) return null
              const pagadoContrato = totalPagadoPorContrato(pagos, contrato.id)
              const saldo = Math.max(0, contrato.montoTotal - pagadoContrato)
              const pct = percent(pagadoContrato, contrato.montoTotal)
              const pagosContrato = pagosDeContrato(pagos, contrato.id)
              return (
                <div className="rounded-card border border-line p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-bold text-ink">Contrato #{contrato.id}</p>
                    <Badge tone={ESTADO_CONTRATO_TONE[contrato.estado] as 'live' | 'danger'} size="sm" dot>{contrato.estado}</Badge>
                  </div>
                  <p className="mt-1 text-[11px] text-ink-muted">{formatDate(contrato.inicio)} — {formatDate(contrato.fin)}</p>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                    <div><p className="text-[10px] text-ink-muted">Total</p><p className="tabular text-sm font-bold text-ink">{formatMoney(contrato.montoTotal)}</p></div>
                    <div><p className="text-[10px] text-ink-muted">Pagado</p><p className="tabular text-sm font-bold text-live">{formatMoney(pagadoContrato)}</p></div>
                    <div><p className="text-[10px] text-ink-muted">Pendiente</p><p className="tabular text-sm font-bold text-time">{formatMoney(saldo)}</p></div>
                  </div>
                  <Progress value={pct} tone="live" className="mt-3" />
                  <div className="mt-4">
                    <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Pagos recientes</p>
                    {pagosContrato.length === 0 ? (
                      <p className="mt-2 text-xs text-ink-muted">Sin pagos registrados.</p>
                    ) : (
                      <div className="mt-2 space-y-1.5">
                        {pagosContrato.map((pago) => (
                          <div key={pago.id} className="flex items-center justify-between rounded-control bg-sunken/35 px-3 py-2">
                            <div>
                              <p className="text-xs font-semibold text-ink">{pago.referencia}</p>
                              <p className="text-[10px] text-ink-muted">{formatDate(pago.fecha)} · {pago.tipo}</p>
                            </div>
                            <p className="tabular text-xs font-bold text-live">{formatMoney(pago.monto)}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })()}
          </div>
        )}
      </Drawer>

      <ConfirmDialog
        open={Boolean(toDelete)}
        onOpenChange={(open) => !open && setToDelete(null)}
        title="Eliminar patrocinante"
        description={toDelete ? `Se eliminará "${toDelete.nombre}" del directorio comercial.` : ''}
        confirmLabel="Eliminar"
        onConfirm={confirmarEliminar}
      />
    </div>
  )
}

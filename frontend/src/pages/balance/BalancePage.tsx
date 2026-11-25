import { zodResolver } from '@hookform/resolvers/zod'
import {
  CalendarClock,
  Download,
  Eye,
  FileText,
  Landmark,
  Pencil,
  Plus,
  Printer,
  Trash2,
  TrendingUp,
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
import { EmptyState } from '@/components/ui/EmptyState'
import { Input, Textarea } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Progress } from '@/components/ui/Progress'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SearchInput } from '@/components/ui/SearchInput'
import { SegmentedControl } from '@/components/ui/SegmentedControl'
import { Select } from '@/components/ui/Select'
import { Logo } from '@/components/brand/Logo'
import { useData } from '@/hooks/useData'
import {
  DEMO_TODAY_ISO,
  ESTADO_CONTRATO_TONE,
  TIPO_PAGO_OPTIONS,
} from '@/lib/constants'
import { formatDate, formatMoney, formatMoneyExact, percent } from '@/lib/format'
import { pagoSchema, type PagoForm } from '@/lib/schemas'
import {
  pagosDeContrato,
  saldoContrato,
  totalContratado,
  totalPagado,
  totalPagadoPorContrato,
} from '@/lib/selectors'
import type { Contrato, Pago } from '@/types'

function PagoFormModal({
  open,
  onOpenChange,
  contratoInicial,
  pago,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  contratoInicial: number | null
  pago: Pago | null
}) {
  const { contratos, patrocinadores, pagos, addPago, updatePago } = useData()

  const contratosDisponibles = useMemo(
    () =>
      contratos
        .filter((contrato) => pago?.contratoId === contrato.id || saldoContrato(contrato, pagos) > 0)
        .map((contrato) => {
          const patrocinador = patrocinadores.find((item) => item.id === contrato.patrocinadorId)
          return {
            value: String(contrato.id),
            label: `${patrocinador?.nombre ?? `Contrato #${contrato.id}`} · saldo ${formatMoney(saldoContrato(contrato, pagos))}`,
          }
        }),
    [contratos, pagos, patrocinadores, pago],
  )

  const form = useForm<PagoForm>({
    resolver: zodResolver(pagoSchema),
    defaultValues: {
      contratoId: pago ? String(pago.contratoId) : contratoInicial ? String(contratoInicial) : '',
      monto: pago?.monto ?? 0,
      tipoPago: pago?.tipo ?? 'Transferencia',
      referencia: pago?.referencia ?? '',
      fecha: pago?.fecha ?? DEMO_TODAY_ISO,
      hora: pago?.hora ?? '12:00',
      descripcion: pago?.descripcion ?? '',
    },
  })

  const contratoId = form.watch('contratoId')
  const monto = form.watch('monto')
  const contrato = contratos.find((item) => String(item.id) === contratoId)
  const patrocinador = patrocinadores.find((item) => item.id === contrato?.patrocinadorId)
  const pagadoContrato = contrato ? totalPagadoPorContrato(pagos, contrato.id) : 0
  const saldoBase = contrato ? contrato.montoTotal - pagadoContrato : 0
  const saldoDisponible = contrato ? saldoBase + (pago?.contratoId === contrato.id ? pago.monto : 0) : 0
  const nuevoSaldo = contrato ? Math.max(0, saldoDisponible - (Number.isFinite(monto) ? monto : 0)) : 0

  const onSubmit = (values: PagoForm) => {
    if (!contrato) {
      form.setError('contratoId', { message: 'Selecciona un contrato' })
      return
    }
    if (values.monto > saldoDisponible) {
      form.setError('monto', { message: `El monto excede el saldo disponible (${formatMoney(saldoDisponible)})` })
      return
    }
    const input = {
      contratoId: Number(values.contratoId),
      monto: values.monto,
      tipo: values.tipoPago as Pago['tipo'],
      referencia: values.referencia,
      fecha: values.fecha,
      hora: values.hora,
      descripcion: values.descripcion,
    }
    if (pago) {
      updatePago(pago.id, input)
      toast.success('Pago actualizado')
    } else {
      addPago(input)
      toast.success('Pago registrado', { description: `Nuevo saldo: ${formatMoney(nuevoSaldo)}` })
    }
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={pago ? 'Editar pago' : 'Registrar pago'}
      description="Abono asociado a un contrato de patrocinio."
      icon={Wallet}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {pago ? 'Guardar cambios' : 'Registrar pago'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
        <Controller
          control={form.control}
          name="contratoId"
          render={({ field }) => (
            <Select
              label="Contrato"
              placeholder="Selecciona un contrato"
              options={contratosDisponibles}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.contratoId?.message}
              disabled={Boolean(pago)}
              className="sm:col-span-2"
            />
          )}
        />

        {contrato && (
          <div className="rounded-control border border-line bg-sunken/35 p-3 sm:col-span-2">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Contrato #{contrato.id}</p>
                <p className="text-sm font-bold text-ink">{patrocinador?.nombre ?? 'Sin patrocinador'}</p>
              </div>
              <Badge tone={ESTADO_CONTRATO_TONE[contrato.estado] as 'live' | 'danger'} size="sm" dot>
                {contrato.estado}
              </Badge>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-[10px] text-ink-muted">Total</p>
                <p className="tabular text-sm font-bold text-ink">{formatMoney(contrato.montoTotal)}</p>
              </div>
              <div>
                <p className="text-[10px] text-ink-muted">Pagado</p>
                <p className="tabular text-sm font-bold text-live">{formatMoney(pagadoContrato)}</p>
              </div>
              <div>
                <p className="text-[10px] text-ink-muted">Disponible</p>
                <p className="tabular text-sm font-bold text-time">{formatMoney(saldoDisponible)}</p>
              </div>
            </div>
            <Progress value={percent(pagadoContrato, contrato.montoTotal)} tone="live" size="sm" className="mt-3" />
          </div>
        )}

        <Input
          label="Monto"
          type="number"
          min={0}
          step="0.01"
          placeholder="0.00"
          error={form.formState.errors.monto?.message}
          hint={contrato ? `Disponible: ${formatMoney(saldoDisponible)}` : undefined}
          {...form.register('monto', { valueAsNumber: true })}
        />
        <Controller
          control={form.control}
          name="tipoPago"
          render={({ field }) => (
            <Select
              label="Tipo de pago"
              options={TIPO_PAGO_OPTIONS.map((option) => ({ value: option.value, label: option.label }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.tipoPago?.message}
            />
          )}
        />
        <Input
          label="Referencia"
          placeholder="TRF-2026-000"
          error={form.formState.errors.referencia?.message}
          {...form.register('referencia')}
        />
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Fecha"
            type="date"
            error={form.formState.errors.fecha?.message}
            {...form.register('fecha')}
          />
          <Input
            label="Hora"
            type="time"
            error={form.formState.errors.hora?.message}
            {...form.register('hora')}
          />
        </div>
        <Textarea
          label="Notas"
          placeholder="Detalle del abono..."
          className="sm:col-span-2"
          error={form.formState.errors.descripcion?.message}
          {...form.register('descripcion')}
        />

        {contrato && (
          <div className="flex items-center justify-between rounded-control border border-line bg-sunken/35 px-3 py-2 text-xs sm:col-span-2">
            <span className="text-ink-muted">Saldo después del pago</span>
            <span className="tabular font-bold text-ink">{formatMoney(nuevoSaldo)}</span>
          </div>
        )}
      </form>
    </Modal>
  )
}

export function BalancePage() {
  const {
    contratos,
    pagos,
    patrocinadores,
    deletePago,
  } = useData()
  const [searchParams, setSearchParams] = useSearchParams()
  const [filter, setFilter] = useState('todos')
  const [search, setSearch] = useState('')
  const [pagoOpen, setPagoOpen] = useState(() => searchParams.get('pago') === '1')
  const [pagoEditing, setPagoEditing] = useState<Pago | null>(null)
  const [contratoInicial, setContratoInicial] = useState<number | null>(null)
  const [statement, setStatement] = useState<Contrato | null>(null)
  const [toDeletePago, setToDeletePago] = useState<Pago | null>(null)

  const cerrarPago = (open: boolean) => {
    setPagoOpen(open)
    if (!open && searchParams.get('pago')) setSearchParams({}, { replace: true })
  }

  const contratado = totalContratado(contratos)
  const pagado = totalPagado(pagos)
  const saldo = Math.max(0, contratado - pagado)
  const activos = contratos.filter((contrato) => contrato.estado === 'Vigente').length

  const nombrePatrocinador = (contrato: Contrato) =>
    patrocinadores.find((item) => item.id === contrato.patrocinadorId)?.nombre ?? 'Sin patrocinador'

  const contratosFiltrados = useMemo(() => {
    const term = search.trim().toLowerCase()
    return [...contratos]
      .filter((contrato) => {
        const saldoActual = saldoContrato(contrato, pagos)
        const coincideFiltro =
          filter === 'todos' ||
          (filter === 'saldo' && saldoActual > 0) ||
          (filter === 'liquidados' && saldoActual === 0)
        const nombre = patrocinadores.find((item) => item.id === contrato.patrocinadorId)?.nombre ?? ''
        const coincideTexto = !term || nombre.toLowerCase().includes(term)
        return coincideFiltro && coincideTexto
      })
      .sort((a, b) => saldoContrato(b, pagos) - saldoContrato(a, pagos))
  }, [contratos, pagos, patrocinadores, search, filter])

  const pagosFiltrados = useMemo(() => {
    const term = search.trim().toLowerCase()
    return pagos.filter((pago) => {
      if (!term) return true
      const contrato = contratos.find((item) => item.id === pago.contratoId)
      const nombre = contrato
        ? patrocinadores.find((item) => item.id === contrato.patrocinadorId)?.nombre ?? ''
        : ''
      return pago.referencia.toLowerCase().includes(term) || nombre.toLowerCase().includes(term)
    })
  }, [pagos, contratos, patrocinadores, search])

  const abrirPago = (contrato?: Contrato) => {
    setPagoEditing(null)
    setContratoInicial(contrato?.id ?? null)
    setPagoOpen(true)
  }

  const editarPago = (pago: Pago) => {
    setPagoEditing(pago)
    setContratoInicial(pago.contratoId)
    setPagoOpen(true)
  }

  const confirmarEliminar = () => {
    if (!toDeletePago) return
    deletePago(toDeletePago.id)
    toast.success('Pago eliminado')
    setToDeletePago(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Módulo financiero"
        title="Balance"
        description="Cobranza, pagos y estado de cuenta de cada contrato."
        actions={
          <>
            <Button variant="secondary" size="sm" leftIcon={<Download className="size-3.5" />} onClick={() => toast.success('Reporte de cobranza listo')}>
              Exportar
            </Button>
            <Button size="sm" leftIcon={<Plus className="size-3.5" />} onClick={() => abrirPago()}>
              Registrar pago
            </Button>
          </>
        }
      />

      <ScoreboardStrip
        items={[
          { label: 'Contratado', value: formatMoney(contratado), hint: `${contratos.length} contratos`, tone: 'info', icon: Landmark },
          { label: 'Pagado', value: formatMoney(pagado), hint: `${Math.round(percent(pagado, contratado))}% de avance`, tone: 'live', icon: TrendingUp },
          { label: 'Pendiente', value: formatMoney(saldo), hint: 'Saldo por cobrar', tone: 'time', icon: CalendarClock },
          { label: 'Activos', value: String(activos), hint: `${contratos.length - activos} vencidos`, tone: 'brand', icon: FileText },
        ]}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="space-y-3 lg:col-span-7">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <SearchInput value={search} onChange={setSearch} placeholder="Buscar marca o referencia" className="sm:max-w-xs" />
            <SegmentedControl
              value={filter}
              onValueChange={setFilter}
              ariaLabel="Filtrar contratos"
              options={[
                { value: 'todos', label: 'Todos' },
                { value: 'saldo', label: 'Con saldo' },
                { value: 'liquidados', label: 'Liquidados' },
              ]}
            />
          </div>

          {contratosFiltrados.length === 0 ? (
            <EmptyState
              icon={Wallet}
              title="Sin contratos"
              description="No hay contratos que coincidan con el filtro seleccionado."
            />
          ) : (
            <div className="space-y-3">
              {contratosFiltrados.map((contrato) => {
                const pagadoContrato = totalPagadoPorContrato(pagos, contrato.id)
                const saldoContratoActual = saldoContrato(contrato, pagos)
                const pct = percent(pagadoContrato, contrato.montoTotal)
                return (
                  <Card key={contrato.id} className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex min-w-0 items-center gap-3">
                        <Avatar name={nombrePatrocinador(contrato)} size="md" />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-bold text-ink">{nombrePatrocinador(contrato)}</p>
                          <p className="text-[11px] text-ink-muted">Contrato #{contrato.id} · {formatDate(contrato.inicio)} — {formatDate(contrato.fin)}</p>
                        </div>
                      </div>
                      <Badge tone={ESTADO_CONTRATO_TONE[contrato.estado] as 'live' | 'danger'} size="sm" dot>
                        {contrato.estado}
                      </Badge>
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-[10px] uppercase tracking-wide text-ink-muted">Total</p>
                        <p className="tabular text-sm font-bold text-ink">{formatMoney(contrato.montoTotal)}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-wide text-ink-muted">Pagado</p>
                        <p className="tabular text-sm font-bold text-live">{formatMoney(pagadoContrato)}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-wide text-ink-muted">Pendiente</p>
                        <p className="tabular text-sm font-bold text-time">{formatMoney(saldoContratoActual)}</p>
                      </div>
                    </div>
                    <Progress value={pct} tone="live" className="mt-3" />
                    <div className="mt-3 flex items-center justify-between">
                      <span className="text-[10px] text-ink-muted">{Math.round(pct)}% cobrado</span>
                      <div className="flex items-center gap-1.5">
                        <Button variant="ghost" size="sm" leftIcon={<Eye className="size-3.5" />} onClick={() => setStatement(contrato)}>
                          Estado
                        </Button>
                        <Button variant="secondary" size="sm" leftIcon={<Plus className="size-3.5" />} onClick={() => abrirPago(contrato)} disabled={saldoContratoActual === 0}>
                          Abonar
                        </Button>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>
          )}
        </div>

        <Card className="h-fit self-start overflow-hidden lg:sticky lg:top-20 lg:col-span-5">
          <div className="border-b border-line p-4">
            <p className="text-sm font-bold text-ink">Pagos recientes</p>
            <p className="text-[11px] text-ink-muted">{pagosFiltrados.length} movimientos registrados</p>
          </div>
          <div className="max-h-[560px] divide-y divide-line overflow-y-auto scroll-area">
            {pagosFiltrados.length === 0 ? (
              <div className="p-5">
                <EmptyState icon={Wallet} title="Sin pagos" description="No hay pagos que coincidan con la búsqueda." />
              </div>
            ) : (
              pagosFiltrados.map((pago) => {
                const contrato = contratos.find((item) => item.id === pago.contratoId)
                return (
                  <div key={pago.id} className="flex items-start gap-3 p-4">
                    <span className="grid size-8 shrink-0 place-items-center rounded-control bg-live-soft text-live">
                      <Wallet className="size-3.5" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-ink">
                        {contrato ? nombrePatrocinador(contrato) : `Contrato #${pago.contratoId}`}
                      </p>
                      <p className="truncate text-[10px] text-ink-muted">
                        {pago.referencia} · {formatDate(pago.fecha)} · {pago.tipo}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="tabular text-xs font-bold text-live">{formatMoneyExact(pago.monto)}</p>
                      <div className="mt-1 flex items-center justify-end gap-0.5">
                        <Button variant="ghost" size="icon" className="size-7" aria-label="Editar pago" onClick={() => editarPago(pago)}>
                          <Pencil className="size-3" />
                        </Button>
                        <Button variant="ghost" size="icon" className="size-7" aria-label="Eliminar pago" onClick={() => setToDeletePago(pago)}>
                          <Trash2 className="size-3 text-danger" />
                        </Button>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </Card>
      </div>

      {pagoOpen && (
        <PagoFormModal
          key={pagoEditing?.id ?? `nuevo-${contratoInicial ?? 'libre'}`}
          open={pagoOpen}
          onOpenChange={cerrarPago}
          contratoInicial={contratoInicial}
          pago={pagoEditing}
        />
      )}

      <Modal
        open={Boolean(statement)}
        onOpenChange={(open) => !open && setStatement(null)}
        title="Estado de cuenta"
        description={statement ? `${nombrePatrocinador(statement)} · Contrato #${statement.id}` : undefined}
        icon={FileText}
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={() => setStatement(null)}>Cerrar</Button>
            <Button onClick={() => window.print()} leftIcon={<Printer className="size-4" />}>Imprimir</Button>
          </>
        }
      >
        {statement && (() => {
          const pagadoContrato = totalPagadoPorContrato(pagos, statement.id)
          const saldoActual = saldoContrato(statement, pagos)
          const listaPagos = pagosDeContrato(pagos, statement.id)
          return (
            <div className="print-area rounded-card bg-white p-6 text-[#0b1424]">
              <div className="flex items-start justify-between gap-4 border-b border-[#d9dee6] pb-4">
                <Logo size="sm" tone="default" />
                <div className="text-right">
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#647187]">Estado de cuenta</p>
                  <p className="text-sm font-bold">Contrato #{statement.id}</p>
                  <p className="text-xs text-[#647187]">{formatDate(statement.inicio)} — {formatDate(statement.fin)}</p>
                </div>
              </div>
              <div className="mt-4 flex items-start justify-between">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#647187]">Patrocinante</p>
                  <p className="text-base font-bold">{nombrePatrocinador(statement)}</p>
                </div>
                <Badge tone={ESTADO_CONTRATO_TONE[statement.estado] as 'live' | 'danger'} size="sm">
                  {statement.estado}
                </Badge>
              </div>
              <div className="mt-5 grid grid-cols-3 gap-2 rounded-control border border-[#d9dee6] p-3 text-center">
                <div>
                  <p className="text-[10px] uppercase tracking-wide text-[#647187]">Monto total</p>
                  <p className="tabular text-sm font-bold">{formatMoneyExact(statement.montoTotal)}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wide text-[#647187]">Pagado</p>
                  <p className="tabular text-sm font-bold text-[#19875f]">{formatMoneyExact(pagadoContrato)}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wide text-[#647187]">Pendiente</p>
                  <p className="tabular text-sm font-bold text-[#a8640b]">{formatMoneyExact(saldoActual)}</p>
                </div>
              </div>
              <table className="mt-5 w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-[#d9dee6] text-[10px] uppercase tracking-wide text-[#647187]">
                    <th className="py-2 pr-2">Fecha</th>
                    <th className="py-2 pr-2">Referencia</th>
                    <th className="py-2 pr-2">Tipo</th>
                    <th className="py-2 text-right">Monto</th>
                  </tr>
                </thead>
                <tbody>
                  {listaPagos.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-[#647187]">Sin pagos registrados.</td>
                    </tr>
                  ) : (
                    listaPagos.map((pago) => (
                      <tr key={pago.id} className="border-b border-[#e8ecf1]">
                        <td className="py-2 pr-2">{formatDate(pago.fecha)}</td>
                        <td className="py-2 pr-2 font-mono">{pago.referencia}</td>
                        <td className="py-2 pr-2">{pago.tipo}</td>
                        <td className="tabular py-2 text-right font-semibold">{formatMoneyExact(pago.monto)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
              <p className="mt-6 border-t border-[#d9dee6] pt-3 text-center text-[10px] text-[#647187]">
                Itinerario · Palco de Operaciones · Estadio Antonio Herrera Gutiérrez
              </p>
            </div>
          )
        })()}
      </Modal>

      <ConfirmDialog
        open={Boolean(toDeletePago)}
        onOpenChange={(open) => !open && setToDeletePago(null)}
        title="Eliminar pago"
        description={toDeletePago ? `Se eliminará el pago ${toDeletePago.referencia} de ${formatMoneyExact(toDeletePago.monto)}.` : ''}
        confirmLabel="Eliminar"
        onConfirm={confirmarEliminar}
      />
    </div>
  )
}

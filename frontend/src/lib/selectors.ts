import type { Contrato, Pago, Recurso, Tarea } from '@/types'

const MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

export function pagosDeContrato(pagos: Pago[], contratoId: number) {
  return pagos.filter((pago) => pago.contratoId === contratoId)
}

export function totalPagadoPorContrato(pagos: Pago[], contratoId: number) {
  return pagosDeContrato(pagos, contratoId).reduce((total, pago) => total + pago.monto, 0)
}

export function totalPagado(pagos: Pago[]) {
  return pagos.reduce((total, pago) => total + pago.monto, 0)
}

export function totalContratado(contratos: Contrato[]) {
  return contratos.reduce((total, contrato) => total + contrato.montoTotal, 0)
}

export function saldoContrato(contrato: Contrato, pagos: Pago[]) {
  return Math.max(0, contrato.montoTotal - totalPagadoPorContrato(pagos, contrato.id))
}

export function contratoDePatrocinador(contratos: Contrato[], patrocinadorId: number) {
  return contratos.find((contrato) => contrato.patrocinadorId === patrocinadorId)
}

export function pagosPorMes(pagos: Pago[]) {
  const acumulado = new Map<string, number>()
  for (const pago of pagos) {
    const clave = pago.fecha.slice(0, 7)
    acumulado.set(clave, (acumulado.get(clave) ?? 0) + pago.monto)
  }
  return [...acumulado.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([clave, total]) => ({
      mes: MESES[Number(clave.slice(5, 7)) - 1],
      total,
    }))
}

export function tareasPorEstado(tareas: Tarea[]) {
  const estados = ['Pendiente', 'En progreso', 'Completada'] as const
  return estados.map((estado) => ({
    estado,
    value: tareas.filter((tarea) => tarea.estado === estado).length,
  }))
}

export function recursosPorEstado(recursos: Recurso[]) {
  return {
    disponibles: recursos.filter((recurso) => recurso.estado === 'Disponible').length,
    asignados: recursos.filter((recurso) => recurso.estado === 'Asignado').length,
    mantenimiento: recursos.filter((recurso) => recurso.estado === 'En mantenimiento').length,
    total: recursos.length,
    valor: recursos.reduce((total, recurso) => total + recurso.costo, 0),
  }
}

export function duracionGuion(elementos: { duracion: number }[]) {
  return elementos.reduce((total, elemento) => total + elemento.duracion, 0)
}

export function progresoElementos(elementos: { estado: string }[]) {
  if (elementos.length === 0) return 0
  return Math.round((elementos.filter((elemento) => elemento.estado === 'Completado').length / elementos.length) * 100)
}

export function contarFases(elementos: { tipo: string }[]) {
  return {
    prejuego: elementos.filter((elemento) => elemento.tipo === 'Prejuego').length,
    juego: elementos.filter((elemento) => elemento.tipo === 'Juego').length,
    postjuego: elementos.filter((elemento) => elemento.tipo === 'Postjuego').length,
  }
}

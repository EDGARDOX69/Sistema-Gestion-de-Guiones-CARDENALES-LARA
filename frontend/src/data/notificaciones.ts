import type { Actividad, Notificacion } from '@/types'

export const NOTIFICACIONES: Notificacion[] = [
  {
    id: 1,
    tipo: 'tarea',
    titulo: 'Tarea asignada',
    mensaje: 'Te asignaron: Confirmar pauta de Banesco en el inning 3.',
    tiempo: 'Hace 5 min',
    leida: false,
  },
  {
    id: 2,
    tipo: 'pago',
    titulo: 'Pago registrado',
    mensaje: 'Se registró un abono de $21.250 para Maltin Polar.',
    tiempo: 'Hace 1 h',
    leida: true,
  },
  {
    id: 3,
    tipo: 'guion',
    titulo: 'Guion publicado',
    mensaje: 'Cardenales vs Tiburones está listo para el 12 de julio.',
    tiempo: 'Hace 2 h',
    leida: false,
  },
  {
    id: 4,
    tipo: 'sistema',
    titulo: 'Show en vivo',
    mensaje: 'Cardenales vs Leones inició a las 5:00 PM.',
    tiempo: 'Hace 18 min',
    leida: true,
  },
]

export const ACTIVIDAD: Actividad[] = [
  {
    id: 1,
    tipo: 'sistema',
    titulo: 'Show iniciado',
    detalle: 'Cardenales vs Leones · Estadio Antonio Herrera Gutiérrez',
    tiempo: 'Hace 18 min',
    usuario: 'Keiver',
  },
  {
    id: 2,
    tipo: 'pago',
    titulo: 'Pago registrado',
    detalle: 'Maltin Polar · $21.250 · TRF-2026-002',
    tiempo: 'Hace 42 min',
    usuario: 'Keiver',
  },
  {
    id: 3,
    tipo: 'guion',
    titulo: 'Guion publicado',
    detalle: 'Cardenales vs Tiburones · 12 de julio',
    tiempo: 'Hace 1 h',
    usuario: 'Genesis',
  },
  {
    id: 4,
    tipo: 'tarea',
    titulo: 'Tarea completada',
    detalle: 'Verificar equipo de transmisión',
    tiempo: 'Hace 2 h',
    usuario: 'Keiver',
  },
  {
    id: 5,
    tipo: 'patrocinador',
    titulo: 'Patrocinante actualizado',
    detalle: 'Banesco Banco Universal · Contrato #5',
    tiempo: 'Hace 3 h',
    usuario: 'Naryi',
  },
  {
    id: 6,
    tipo: 'inventario',
    titulo: 'Recurso asignado',
    detalle: 'Sony PXW-Z150 · Keiver Zamudio',
    tiempo: 'Hace 4 h',
    usuario: 'Genesis',
  },
]

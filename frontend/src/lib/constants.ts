import type { ModuleId, Prioridad, TipoContrato, TipoPago } from '@/types'

export const APP_NAME = 'Itinerario'
export const APP_SUBTITLE = 'Palco de Operaciones'
export const STADIUM_NAME = 'Estadio Antonio Herrera Gutiérrez'
export const STADIUM_CITY = 'Barquisimeto, Venezuela'
export const DEMO_DATE = new Date('2026-07-10T12:00:00-04:00')
export const DEMO_TODAY_ISO = '2026-07-10'
export const CAPTCHA_LENGTH = 4

// El CAPTCHA del demo esta desactivado por defecto;activarlo con VITE_CAPTCHA_ENABLED=1.
const variableActiva = (valor: string | undefined) =>
  ['1', 'true', 'yes', 'on'].includes((valor ?? '').trim().toLowerCase())

export const CAPTCHA_ENABLED = variableActiva(import.meta.env.VITE_CAPTCHA_ENABLED)

export const STORAGE_KEYS = {
  session: 'itinerario.session',
  module: 'itinerario.module',
  theme: 'itinerario.theme',
} as const

export const TIPO_CONTRATO_LABEL: Record<TipoContrato, string> = {
  1: 'Patrocinio',
  2: 'Publicidad',
  3: 'Mixto',
}

export const TIPO_CONTRATO_OPTIONS = [
  { value: '1', label: TIPO_CONTRATO_LABEL[1] },
  { value: '2', label: TIPO_CONTRATO_LABEL[2] },
  { value: '3', label: TIPO_CONTRATO_LABEL[3] },
]

export const TIPO_PAGO_OPTIONS: { value: TipoPago; label: TipoPago }[] = [
  { value: 'Transferencia', label: 'Transferencia' },
  { value: 'Efectivo', label: 'Efectivo' },
  { value: 'Cheque', label: 'Cheque' },
  { value: 'Depósito', label: 'Depósito' },
]

export const ESTADO_RECURSO_OPTIONS = [
  { value: 'Disponible', label: 'Disponible' },
  { value: 'Asignado', label: 'Asignado' },
  { value: 'En mantenimiento', label: 'En mantenimiento' },
  { value: 'Dañado', label: 'Dañado' },
  { value: 'Baja', label: 'Baja' },
]

export const PRIORIDAD_OPTIONS: { value: Prioridad; label: Prioridad }[] = [
  { value: 'Alta', label: 'Alta' },
  { value: 'Media', label: 'Media' },
  { value: 'Baja', label: 'Baja' },
]

export const DEPARTAMENTOS = [
  'Medios',
  'Palco de Operaciones',
  'Producción',
  'Técnica',
  'Comercial',
  'Administración',
  'Operaciones',
]

export const ROLES = ['Superadmin', 'Administrador', 'Usuario']

export const MODULOS: { id: ModuleId; nombre: string; descripcion: string; ruta: string }[] = [
  {
    id: 'patrocinantes',
    nombre: 'Patrocinantes',
    descripcion: 'Marcas, contratos y contacto comercial.',
    ruta: '/app/patrocinantes',
  },
  {
    id: 'balance',
    nombre: 'Balance',
    descripcion: 'Cobranza, pagos y estado de cuenta.',
    ruta: '/app/balance',
  },
  {
    id: 'inventario',
    nombre: 'Inventario',
    descripcion: 'Recursos, tipos y asignaciones.',
    ruta: '/app/inventario',
  },
  {
    id: 'tareas',
    nombre: 'Tareas',
    descripcion: 'Asignaciones y avance de la jornada.',
    ruta: '/app/tareas',
  },
  {
    id: 'guion',
    nombre: 'Guion',
    descripcion: 'Guiones del juego y control en vivo.',
    ruta: '/app/guion',
  },
]

export const MODULO_POR_ID = Object.fromEntries(MODULOS.map((modulo) => [modulo.id, modulo])) as Record<
  ModuleId,
  (typeof MODULOS)[number]
>

export const MODULE_ACCENT: Record<
  ModuleId,
  { text: string; bg: string; border: string; dot: string }
> = {
  patrocinantes: {
    text: 'text-brand',
    bg: 'bg-brand-soft',
    border: 'border-brand/30',
    dot: 'bg-brand',
  },
  balance: {
    text: 'text-live',
    bg: 'bg-live-soft',
    border: 'border-live/30',
    dot: 'bg-live',
  },
  inventario: {
    text: 'text-info',
    bg: 'bg-info-soft',
    border: 'border-info/30',
    dot: 'bg-info',
  },
  tareas: {
    text: 'text-time',
    bg: 'bg-time-soft',
    border: 'border-time/30',
    dot: 'bg-time',
  },
  guion: {
    text: 'text-brand',
    bg: 'bg-brand-soft',
    border: 'border-brand/30',
    dot: 'bg-brand',
  },
}

export const ESTADO_TAREA_TONE: Record<string, string> = {
  Pendiente: 'time',
  'En progreso': 'info',
  Completada: 'live',
}

export const ESTADO_RECURSO_TONE: Record<string, string> = {
  Disponible: 'live',
  Asignado: 'info',
  'En mantenimiento': 'time',
  Dañado: 'danger',
  Baja: 'neutral',
}

export const PRIORIDAD_TONE: Record<string, string> = {
  Alta: 'danger',
  Media: 'time',
  Baja: 'info',
}

export const ESTADO_GUION_TONE: Record<string, string> = {
  Borrador: 'neutral',
  Publicado: 'info',
  'En vivo': 'live',
}

export const ESTADO_ELEMENTO_TONE: Record<string, string> = {
  Pendiente: 'neutral',
  'En curso': 'time',
  Completado: 'live',
}

export const ESTADO_CONTRATO_TONE: Record<string, string> = {
  Vigente: 'live',
  Vencido: 'danger',
}

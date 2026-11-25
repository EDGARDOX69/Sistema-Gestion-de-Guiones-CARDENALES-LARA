export type ModuleId = 'patrocinantes' | 'balance' | 'inventario' | 'tareas' | 'guion'

export type TipoContrato = 1 | 2 | 3

export type EstadoContrato = 'Vigente' | 'Vencido'

export type TipoPago = 'Transferencia' | 'Efectivo' | 'Cheque' | 'Depósito'

export type EstadoRecurso = 'Disponible' | 'Asignado' | 'En mantenimiento' | 'Dañado' | 'Baja'

export type EstadoAsignacion = 'Pendiente' | 'Devuelto' | 'Vencido'

export type EstadoTarea = 'Pendiente' | 'En progreso' | 'Completada'

export type Prioridad = 'Alta' | 'Media' | 'Baja'

export type EstadoGuion = 'Borrador' | 'Publicado' | 'En vivo'

export type FaseGuion = 'Prejuego' | 'Juego' | 'Postjuego'

export type EstadoElemento = 'Pendiente' | 'En curso' | 'Completado'

export type MedioInning = 'Alta' | 'Baja'

export type EstadoShow = 'idle' | 'live'

export type TipoNotificacion = 'tarea' | 'pago' | 'guion' | 'sistema'

export type TipoActividad = 'pago' | 'guion' | 'tarea' | 'patrocinador' | 'inventario' | 'sistema'

export interface Patrocinador {
  id: number
  nombre: string
  rif: string
  tipoContrato: TipoContrato
  contacto: string
  telefono: string
  email: string
  encargadoId: number
  estado: boolean
}

export interface Contrato {
  id: number
  patrocinadorId: number
  inicio: string
  fin: string
  estado: EstadoContrato
  tipo: TipoContrato
  montoTotal: number
}

export interface Pago {
  id: number
  contratoId: number
  monto: number
  tipo: TipoPago
  referencia: string
  fecha: string
  hora: string
  registradoPor: number
  descripcion: string
}

export interface TipoRecurso {
  id: number
  nombre: string
  descripcion: string
}

export interface Recurso {
  id: number
  nombre: string
  descripcion: string
  tipoId: number
  estado: EstadoRecurso
  fechaCompra: string
  costo: number
}

export interface Asignacion {
  id: number
  recursoId: number
  usuarioId: number
  fechaAsignacion: string
  fechaDevolucionEsperada: string
  fechaDevolucionReal: string | null
  estado: EstadoAsignacion
  notas: string
}

export interface Tarea {
  id: number
  nombre: string
  instruccion: string
  creadorId: number
  asignadoId: number
  estado: EstadoTarea
  fecha: string
  prioridad: Prioridad
}

export interface ElementoGuion {
  id: number
  tipo: FaseGuion
  hora: string | null
  inning: number | null
  medioInning: MedioInning | null
  contenido: string
  duracion: number
  encargado: string
  orden: number
  estado: EstadoElemento
}

export interface Guion {
  id: number
  nombre: string
  fecha: string
  estado: EstadoGuion
  tiempoInning: number
  modificado: string
  elementos: ElementoGuion[]
}

export interface Usuario {
  id: number
  nombre: string
  email: string
  cedula: string
  rol: string
  departamento: string
  telefono: string
  activo: boolean
  ultimoAcceso: string
  iniciales: string
}

export interface Notificacion {
  id: number
  tipo: TipoNotificacion
  titulo: string
  mensaje: string
  tiempo: string
  leida: boolean
}

export interface Actividad {
  id: number
  tipo: TipoActividad
  titulo: string
  detalle: string
  tiempo: string
  usuario: string
}

export interface ModuloInfo {
  id: ModuleId
  nombre: string
  descripcion: string
  ruta: string
}

export interface SesionUsuario {
  id: number
  nombre: string
  email: string
  rol: string
  departamento: string
  telefono: string
  cedula: string
  iniciales: string
  ultimoAcceso: string
}

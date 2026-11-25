import { z } from 'zod'

import { CAPTCHA_ENABLED } from '@/lib/constants'

const passwordPolicy = z
  .string()
  .min(8, 'La contraseña debe tener al menos 8 caracteres')
  .regex(/[A-Z]/, 'Debe incluir al menos una mayúscula')
  .regex(/[a-z]/, 'Debe incluir al menos una minúscula')
  .regex(/[0-9]/, 'Debe incluir al menos un número')

const requiredNumber = (message: string) => z.number({ error: message })

const captchaField = CAPTCHA_ENABLED
  ? z.string().length(4, 'Escribe los 4 caracteres del CAPTCHA')
  : z.string().optional()

export const loginSchema = z.object({
  email: z.email('Ingresa un correo válido'),
  password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
  captcha: captchaField,
})

export const forgotSchema = z.object({
  email: z.email('Ingresa un correo válido'),
  captcha: captchaField,
})

export const resetSchema = z
  .object({
    password: passwordPolicy,
    confirm: z.string().min(8, 'Confirma la contraseña'),
  })
  .refine((data) => data.password === data.confirm, {
    path: ['confirm'],
    message: 'Las contraseñas no coinciden',
  })

export const patrocinadorSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(100, 'Máximo 100 caracteres'),
  rif: z.string().regex(/^[JGVEP]-\d{8}-\d$/i, 'Formato de RIF inválido (J-00000000-0)'),
  tipoContrato: z.string().min(1, 'Selecciona un tipo de contrato'),
  contacto: z.string().min(2, 'Indica el nombre del contacto'),
  telefono: z.union([z.literal(''), z.string().regex(/^[0-9()+\-\s]{7,20}$/, 'Teléfono inválido')]),
  email: z.union([z.literal(''), z.email('Correo inválido')]),
  encargadoId: z.string().min(1, 'Selecciona un encargado'),
})

export const pagoSchema = z.object({
  contratoId: z.string().min(1, 'Selecciona un contrato'),
  monto: requiredNumber('Ingresa un monto válido').positive('El monto debe ser mayor a cero'),
  tipoPago: z.string().min(1, 'Selecciona un tipo de pago'),
  referencia: z.string().min(3, 'Indica una referencia'),
  fecha: z.string().min(1, 'Selecciona la fecha'),
  hora: z.string().min(1, 'Selecciona la hora'),
  descripcion: z.string().max(300, 'Máximo 300 caracteres'),
})

export const recursoSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  tipoId: z.string().min(1, 'Selecciona un tipo'),
  descripcion: z.string().max(300, 'Máximo 300 caracteres'),
  fechaCompra: z.string().min(1, 'Selecciona la fecha de compra'),
  costo: requiredNumber('Ingresa un costo válido').min(0, 'El costo no puede ser negativo'),
  estado: z.string().min(1, 'Selecciona un estado'),
})

export const tipoRecursoSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(50, 'Máximo 50 caracteres'),
  descripcion: z.string().max(200, 'Máximo 200 caracteres'),
})

export const asignacionSchema = z.object({
  recursoId: z.string().min(1, 'Selecciona un recurso disponible'),
  usuarioId: z.string().min(1, 'Selecciona un usuario'),
  fechaDevolucion: z.string().min(1, 'Indica la fecha de devolución'),
  notas: z.string().max(300, 'Máximo 300 caracteres'),
})

export const tareaSchema = z.object({
  nombre: z.string().min(3, 'El nombre debe tener al menos 3 caracteres'),
  instruccion: z.string().min(5, 'Describe la instrucción de la tarea'),
  asignadoId: z.string().min(1, 'Selecciona un responsable'),
  fecha: z.string().min(1, 'Selecciona la fecha'),
  prioridad: z.enum(['Alta', 'Media', 'Baja']),
})

export const elementoGuionSchema = z
  .object({
    tipo: z.enum(['Prejuego', 'Juego', 'Postjuego']),
    hora: z.string(),
    inning: requiredNumber('Indica el inning'),
    medioInning: z.string(),
    contenido: z.string().min(3, 'Describe el contenido del elemento'),
    duracion: requiredNumber('Ingresa una duración válida').positive('La duración debe ser mayor a cero'),
    encargado: z.string().min(2, 'Indica el encargado'),
  })
  .superRefine((data, ctx) => {
    if (data.tipo === 'Juego') {
      if (data.inning < 1 || data.inning > 9) {
        ctx.addIssue({ code: 'custom', path: ['inning'], message: 'El inning debe estar entre 1 y 9' })
      }
      if (data.medioInning !== 'Alta' && data.medioInning !== 'Baja') {
        ctx.addIssue({ code: 'custom', path: ['medioInning'], message: 'Selecciona alta o baja' })
      }
    } else if (!data.hora) {
      ctx.addIssue({ code: 'custom', path: ['hora'], message: 'Indica la hora del elemento' })
    }
  })

export const guionSchema = z.object({
  nombre: z.string().min(3, 'El nombre debe tener al menos 3 caracteres'),
  fecha: z.string().min(1, 'Selecciona la fecha del juego'),
  tiempoInning: requiredNumber('Ingresa el tiempo por inning').positive('El tiempo debe ser mayor a cero'),
})

export const usuarioSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  email: z.email('Correo inválido'),
  cedula: z.string().min(6, 'Ingresa la cédula'),
  telefono: z.string().min(7, 'Ingresa el teléfono'),
  rol: z.string().min(1, 'Selecciona un rol'),
  departamento: z.string().min(1, 'Selecciona un departamento'),
  password: z.union([z.literal(''), z.string().min(8, 'La contraseña debe tener al menos 8 caracteres')]),
})

export const perfilSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  email: z.email('Correo inválido'),
  telefono: z.string().min(7, 'Ingresa el teléfono'),
  cedula: z.string().min(6, 'Ingresa la cédula'),
  departamento: z.string().min(1, 'Selecciona un departamento'),
})

export const passwordChangeSchema = z
  .object({
    actual: z.string().min(1, 'Ingresa tu contraseña actual'),
    nueva: passwordPolicy,
    confirmar: z.string().min(8, 'Confirma la nueva contraseña'),
  })
  .refine((data) => data.nueva === data.confirmar, {
    path: ['confirmar'],
    message: 'Las contraseñas no coinciden',
  })

export type LoginForm = z.infer<typeof loginSchema>
export type ForgotForm = z.infer<typeof forgotSchema>
export type ResetForm = z.infer<typeof resetSchema>
export type PatrocinadorForm = z.infer<typeof patrocinadorSchema>
export type PagoForm = z.infer<typeof pagoSchema>
export type RecursoForm = z.infer<typeof recursoSchema>
export type TipoRecursoForm = z.infer<typeof tipoRecursoSchema>
export type AsignacionForm = z.infer<typeof asignacionSchema>
export type TareaForm = z.infer<typeof tareaSchema>
export type ElementoGuionForm = z.infer<typeof elementoGuionSchema>
export type GuionForm = z.infer<typeof guionSchema>
export type UsuarioForm = z.infer<typeof usuarioSchema>
export type PerfilForm = z.infer<typeof perfilSchema>
export type PasswordChangeForm = z.infer<typeof passwordChangeSchema>

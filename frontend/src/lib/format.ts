import { differenceInCalendarDays, format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { CAPTCHA_LENGTH, DEMO_DATE } from '@/lib/constants'

export function formatMoney(value: number) {
  return `$ ${new Intl.NumberFormat('es-VE', { maximumFractionDigits: 0 }).format(value)}`
}

export function formatMoneyExact(value: number) {
  return `$ ${new Intl.NumberFormat('es-VE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)}`
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat('es-VE').format(value)
}

export function formatDate(value: string) {
  return format(parseISO(value), 'd MMM yyyy', { locale: es })
}

export function formatDateShort(value: string) {
  return format(parseISO(value), 'd MMM', { locale: es })
}

export function formatDateLong(value: string | Date) {
  const date = typeof value === 'string' ? parseISO(value) : value
  const text = format(date, "EEEE, d 'de' MMMM 'de' yyyy", { locale: es })
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export function formatMonthShort(value: string) {
  return format(parseISO(value), 'MMM', { locale: es })
}

export function formatTime(value: string | null) {
  if (!value) return ''
  return value.slice(0, 5)
}

export function formatDuration(seconds: number) {
  if (seconds >= 3600) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.round((seconds % 3600) / 60)
    return minutes > 0 ? `${hours} h ${minutes} min` : `${hours} h`
  }
  if (seconds >= 60) {
    const minutes = Math.floor(seconds / 60)
    const rest = seconds % 60
    return rest > 0 ? `${minutes} min ${rest} s` : `${minutes} min`
  }
  return `${seconds} s`
}

export function formatElapsed(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map((part) => String(part).padStart(2, '0')).join(':')
}

export function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  return parts
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
}

export function daysUntil(value: string, from: Date = DEMO_DATE) {
  return differenceInCalendarDays(parseISO(value), from)
}

export function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function percent(part: number, total: number) {
  if (total <= 0) return 0
  return Math.round(Math.min(100, Math.max(0, (part / total) * 100)))
}

export function nombreCorto(nombre: string) {
  return nombre.replace(/\s*-\s*\d{4}-\d{2}-\d{2}$/, '')
}

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function generarCaptcha(
  longitud: number = CAPTCHA_LENGTH,
  caracteres = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789',
) {
  return Array.from({ length: longitud }, () => caracteres[Math.floor(Math.random() * caracteres.length)]).join('')
}

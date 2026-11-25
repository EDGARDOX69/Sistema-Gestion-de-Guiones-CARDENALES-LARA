import { CalendarDays, Radio, ScrollText } from 'lucide-react'
import type { ReactNode } from 'react'
import { FieldLines } from '@/components/brand/FieldLines'
import { Logo } from '@/components/brand/Logo'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { formatDate, formatTime } from '@/lib/format'
import { GUIONES } from '@/data/guiones'

export function AuthShell({
  children,
  heroTitle,
  heroDescription,
}: {
  children: ReactNode
  heroTitle: string
  heroDescription: string
}) {
  const guion = GUIONES[0]
  const totalElementos = guion.elementos.length
  const inicio = guion.elementos.find((elemento) => elemento.tipo === 'Prejuego')?.hora ?? '17:00'

  return (
    <div className="min-h-dvh bg-canvas lg:grid lg:grid-cols-[1.08fr_1fr]">
      <aside className="relative hidden overflow-hidden bg-night-950 p-10 text-chalk lg:flex lg:flex-col lg:justify-between">
        <FieldLines className="absolute -right-24 -top-24 size-[520px] text-white/[0.09]" />
        <div className="absolute inset-0 aurora opacity-70" />
        <div className="relative z-10">
          <Logo size="md" tone="light" />
        </div>

        <div className="relative z-10 max-w-xl">
          <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-chalk/45">Temporada 2026</p>
          <h1 className="display mt-4 text-5xl font-semibold leading-[0.92] text-chalk xl:text-6xl">
            {heroTitle}
          </h1>
          <p className="mt-5 max-w-md text-sm leading-relaxed text-chalk/60">{heroDescription}</p>

          <div className="mt-8 rounded-card border border-white/10 bg-white/[0.04] p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between gap-4">
              <span className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-chalk/55">
                <CalendarDays className="size-3.5" />
                Jornada de hoy
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-live/25 bg-live/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.14em] text-live">
                <span className="size-1.5 rounded-full bg-live live-dot" />
                En vivo
              </span>
            </div>
            <p className="display mt-3 text-2xl font-semibold text-chalk">
              Cardenales <span className="text-chalk/30">vs</span> Leones
            </p>
            <div className="mt-2 flex items-center justify-between text-xs text-chalk/55">
              <span>{formatDate(guion.fecha)}</span>
              <span className="tabular">{formatTime(inicio)}</span>
            </div>
          </div>

          <div className="mt-5 flex items-center gap-6">
            <div className="flex items-center gap-2 text-xs text-chalk/60">
              <ScrollText className="size-4 text-chalk/35" />
              <span className="tabular font-semibold text-chalk">{totalElementos}</span> elementos
            </div>
            <div className="flex items-center gap-2 text-xs text-chalk/60">
              <Radio className="size-4 text-chalk/35" />
              <span className="font-semibold text-chalk">1</span> show activo
            </div>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between text-[10px] font-medium uppercase tracking-[0.16em] text-chalk/35">
          <span>Estadio Antonio Herrera Gutiérrez</span>
          <span>Barquisimeto</span>
        </div>
      </aside>

      <div className="relative flex min-h-dvh flex-col">
        <div className="flex items-center justify-between p-5 lg:justify-end">
          <div className="lg:hidden">
            <Logo size="sm" />
          </div>
          <ThemeToggle />
        </div>
        <div className="flex flex-1 items-center justify-center px-4 pb-10 sm:px-8">
          <div className="w-full max-w-md">{children}</div>
        </div>
        <p className="px-6 pb-6 text-center text-[10px] font-medium uppercase tracking-[0.14em] text-ink-faint">
          Sistema de Gestión de Itinerario · Estadio Antonio Herrera Gutiérrez
        </p>
      </div>
    </div>
  )
}

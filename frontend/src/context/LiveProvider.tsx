import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { GUIONES } from '@/data/guiones'
import type { ElementoGuion, EstadoShow } from '@/types'

export interface FinishSummary {
  total: number
  completed: number
  elapsed: number
}

interface LiveContextValue {
  activeGuionId: number | null
  elements: ElementoGuion[]
  status: EstadoShow
  startedAt: number
  currentElement: ElementoGuion | null
  currentIndex: number
  nextElements: ElementoGuion[]
  completedCount: number
  pendingCount: number
  progress: number
  start: (guionId: number, elementos?: ElementoGuion[]) => void
  advance: () => void
  back: () => void
  finish: () => FinishSummary | null
}

const LiveContext = createContext<LiveContextValue | null>(null)

const initialElements: ElementoGuion[] = GUIONES[0].elementos.map((elemento) => ({ ...elemento }))

export function LiveProvider({ children }: { children: ReactNode }) {
  const [activeGuionId, setActiveGuionId] = useState<number | null>(1)
  const [elements, setElements] = useState<ElementoGuion[]>(initialElements)
  const [status, setStatus] = useState<EstadoShow>('live')
  const [startedAt, setStartedAt] = useState(() => Date.now() - 1122 * 1000)

  const start = useCallback((guionId: number, elementos?: ElementoGuion[]) => {
    const guion = GUIONES.find((item) => item.id === guionId)
    if (!guion) return
    setActiveGuionId(guionId)
    setElements(
      (elementos ?? guion.elementos).map((elemento, index) => ({
        ...elemento,
        estado: index === 0 ? 'En curso' : 'Pendiente',
      })),
    )
    setStartedAt(Date.now())
    setStatus('live')
  }, [])

  const advance = useCallback(() => {
    setElements((prev) => {
      const current = prev.findIndex((elemento) => elemento.estado === 'En curso')
      if (current === -1) {
        const firstPending = prev.findIndex((elemento) => elemento.estado === 'Pendiente')
        if (firstPending === -1) return prev
        return prev.map((elemento, index) =>
          index === firstPending ? { ...elemento, estado: 'En curso' } : elemento,
        )
      }
      const next = prev.findIndex((elemento, index) => index > current && elemento.estado === 'Pendiente')
      return prev.map((elemento, index) => {
        if (index === current) return { ...elemento, estado: 'Completado' }
        if (index === next) return { ...elemento, estado: 'En curso' }
        return elemento
      })
    })
  }, [])

  const back = useCallback(() => {
    setElements((prev) => {
      const current = prev.findIndex((elemento) => elemento.estado === 'En curso')
      if (current <= 0) return prev
      return prev.map((elemento, index) => {
        if (index === current) return { ...elemento, estado: 'Pendiente' }
        if (index === current - 1) return { ...elemento, estado: 'En curso' }
        return elemento
      })
    })
  }, [])

  const finish = useCallback(() => {
    const total = elements.length
    const completed = elements.filter((elemento) => elemento.estado === 'Completado').length
    const elapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000))
    setElements((prev) => prev.map((elemento) => ({ ...elemento, estado: 'Completado' })))
    setStatus('idle')
    setActiveGuionId(null)
    return { total, completed, elapsed }
  }, [elements, startedAt])

  const currentIndex = elements.findIndex((elemento) => elemento.estado === 'En curso')
  const currentElement = currentIndex >= 0 ? elements[currentIndex] : null
  const nextElements = elements
    .filter((elemento, index) => index > currentIndex && elemento.estado === 'Pendiente')
    .slice(0, 4)
  const completedCount = elements.filter((elemento) => elemento.estado === 'Completado').length
  const pendingCount = elements.filter((elemento) => elemento.estado === 'Pendiente').length
  const progress = elements.length > 0 ? Math.round((completedCount / elements.length) * 100) : 0

  const value = useMemo<LiveContextValue>(
    () => ({
      activeGuionId,
      elements,
      status,
      startedAt,
      currentElement,
      currentIndex,
      nextElements,
      completedCount,
      pendingCount,
      progress,
      start,
      advance,
      back,
      finish,
    }),
    [
      activeGuionId,
      elements,
      status,
      startedAt,
      currentElement,
      currentIndex,
      nextElements,
      completedCount,
      pendingCount,
      progress,
      start,
      advance,
      back,
      finish,
    ],
  )

  return <LiveContext.Provider value={value}>{children}</LiveContext.Provider>
}

export function useLiveShow() {
  const context = useContext(LiveContext)
  if (!context) throw new Error('useLiveShow debe usarse dentro de LiveProvider')
  return context
}

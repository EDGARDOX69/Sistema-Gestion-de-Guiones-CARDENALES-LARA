import { useEffect, useState } from 'react'

export function useLiveClock(startedAt: number, active: boolean) {
  const [elapsed, setElapsed] = useState(() => Math.max(0, Math.floor((Date.now() - startedAt) / 1000)))

  useEffect(() => {
    if (!active) return
    const interval = window.setInterval(() => {
      setElapsed(Math.max(0, Math.floor((Date.now() - startedAt) / 1000)))
    }, 1000)
    return () => window.clearInterval(interval)
  }, [startedAt, active])

  return elapsed
}

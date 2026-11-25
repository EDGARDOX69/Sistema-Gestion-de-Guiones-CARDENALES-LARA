import { useCallback, useRef } from 'react'

export function useDoubleTap(callback: () => void, delay = 320) {
  const lastTap = useRef(0)

  return useCallback(() => {
    const now = Date.now()
    if (now - lastTap.current <= delay) {
      lastTap.current = 0
      callback()
      return
    }
    lastTap.current = now
  }, [callback, delay])
}

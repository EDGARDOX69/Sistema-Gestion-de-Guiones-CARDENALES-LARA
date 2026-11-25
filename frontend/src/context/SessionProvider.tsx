import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { STORAGE_KEYS } from '@/lib/constants'
import { DEMO_USER } from '@/data/usuarios'
import type { ModuleId, SesionUsuario } from '@/types'

interface SessionContextValue {
  user: SesionUsuario | null
  selectedModule: ModuleId | null
  login: (email: string) => void
  logout: () => void
  setModule: (module: ModuleId) => void
  clearModule: () => void
  updateUser: (partial: Partial<SesionUsuario>) => void
  isAdmin: boolean
}

const SessionContext = createContext<SessionContextValue | null>(null)

function readSession(): SesionUsuario | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.session)
    if (!raw) return null
    const parsed = JSON.parse(raw) as SesionUsuario
    if (!parsed.id || !parsed.nombre) return null
    return { ...parsed, ultimoAcceso: parsed.ultimoAcceso ?? DEMO_USER.ultimoAcceso }
  } catch {
    return null
  }
}

function readModule(): ModuleId | null {
  const raw = localStorage.getItem(STORAGE_KEYS.module)
  if (raw === 'patrocinantes' || raw === 'balance' || raw === 'inventario' || raw === 'tareas' || raw === 'guion') {
    return raw
  }
  return null
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SesionUsuario | null>(readSession)
  const [selectedModule, setSelectedModule] = useState<ModuleId | null>(readModule)

  const login = useCallback((email: string) => {
    const nextUser: SesionUsuario = {
      id: DEMO_USER.id,
      nombre: DEMO_USER.nombre,
      email,
      rol: DEMO_USER.rol,
      departamento: DEMO_USER.departamento,
      telefono: DEMO_USER.telefono,
      cedula: DEMO_USER.cedula,
      iniciales: DEMO_USER.iniciales,
      ultimoAcceso: DEMO_USER.ultimoAcceso,
    }
    setUser(nextUser)
    localStorage.setItem(STORAGE_KEYS.session, JSON.stringify(nextUser))
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setSelectedModule(null)
    localStorage.removeItem(STORAGE_KEYS.session)
    localStorage.removeItem(STORAGE_KEYS.module)
  }, [])

  const setModule = useCallback((module: ModuleId) => {
    setSelectedModule(module)
    localStorage.setItem(STORAGE_KEYS.module, module)
  }, [])

  const clearModule = useCallback(() => {
    setSelectedModule(null)
    localStorage.removeItem(STORAGE_KEYS.module)
  }, [])

  const updateUser = useCallback((partial: Partial<SesionUsuario>) => {
    setUser((prev) => {
      if (!prev) return prev
      const nombre = partial.nombre ?? prev.nombre
      const next = {
        ...prev,
        ...partial,
        iniciales: nombre
          .split(' ')
          .slice(0, 2)
          .map((part) => part.charAt(0).toUpperCase())
          .join(''),
      }
      localStorage.setItem(STORAGE_KEYS.session, JSON.stringify(next))
      return next
    })
  }, [])

  const value = useMemo(
    () => ({
      user,
      selectedModule,
      login,
      logout,
      setModule,
      clearModule,
      updateUser,
      isAdmin: user?.rol === 'Superadmin',
    }),
    [user, selectedModule, login, logout, setModule, clearModule, updateUser],
  )

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
}

export function useSession() {
  const context = useContext(SessionContext)
  if (!context) throw new Error('useSession debe usarse dentro de SessionProvider')
  return context
}

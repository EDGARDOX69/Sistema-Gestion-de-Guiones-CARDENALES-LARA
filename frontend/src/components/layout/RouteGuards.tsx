import { Navigate, Outlet } from 'react-router-dom'
import { useSession } from '@/hooks/useSession'

export function RequireSession() {
  const { user } = useSession()
  if (!user) return <Navigate to="/login" replace />
  return <Outlet />
}

export function RequireModule() {
  const { selectedModule } = useSession()
  if (!selectedModule) return <Navigate to="/modulos" replace />
  return <Outlet />
}

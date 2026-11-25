import {
  ArrowLeftRight,
  LayoutDashboard,
  LogOut,
  Radio,
  UserRound,
  UsersRound,
} from 'lucide-react'
import type { ComponentType } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Logo } from '@/components/brand/Logo'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { Avatar } from '@/components/ui/Avatar'
import { useLiveClock } from '@/hooks/useLiveClock'
import { useLiveShow } from '@/hooks/useLiveShow'
import { useSession } from '@/hooks/useSession'
import { MODULO_POR_ID, MODULE_ACCENT } from '@/lib/constants'
import { formatElapsed } from '@/lib/format'
import { cn } from '@/lib/cn'
import type { ModuleId } from '@/types'

function NavItem({
  to,
  icon: Icon,
  label,
  exact,
}: {
  to: string
  icon: ComponentType<{ className?: string }>
  label: string
  exact?: boolean
}) {
  const { pathname } = useLocation()
  const isActive = exact ? pathname === to : pathname === to || pathname.startsWith(`${to}/`)

  return (
    <Link
      to={to}
      aria-current={isActive ? 'page' : undefined}
      className={cn(
        'flex h-10 items-center gap-2.5 rounded-control px-3 text-sm font-semibold transition-colors',
        isActive
          ? 'border border-brand/20 bg-brand-soft text-brand'
          : 'text-ink-muted hover:bg-sunken hover:text-ink',
      )}
    >
      <Icon className="size-4" />
      <span className="truncate">{label}</span>
    </Link>
  )
}

export function Sidebar() {
  const { user, selectedModule, isAdmin, clearModule, logout } = useSession()
  const { status, startedAt, activeGuionId } = useLiveShow()
  const elapsed = useLiveClock(startedAt, status === 'live')
  const navigate = useNavigate()
  const moduleInfo = selectedModule ? MODULO_POR_ID[selectedModule] : null
  const accent = selectedModule ? MODULE_ACCENT[selectedModule] : null

  if (!user) return null

  const cambiarModulo = () => {
    clearModule()
    navigate('/modulos')
  }

  const cerrarSesion = () => {
    logout()
    navigate('/login')
    toast.success('Sesión cerrada')
  }

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[260px] flex-col border-r border-line bg-canvas lg:flex">
      <div className="p-5">
        <Link to="/app/dashboard" aria-label="Ir al dashboard">
          <Logo />
        </Link>
      </div>

      {moduleInfo && accent && (
        <div className="px-4">
          <div className={cn('rounded-card border p-3.5', accent.border, accent.bg)}>
            <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-ink-muted">Módulo activo</p>
            <div className="mt-2 flex items-center gap-2.5">
              <span className={cn('grid size-8 place-items-center rounded-control bg-surface', accent.text)}>
                <ModuleIcon id={selectedModule as ModuleId} className="size-4" />
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-bold text-ink">{moduleInfo.nombre}</p>
                <p className="truncate text-[10px] text-ink-muted">Sesión enfocada</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <nav className="scroll-area mt-5 flex-1 space-y-1 overflow-y-auto px-4">
        <NavItem to="/app/dashboard" icon={LayoutDashboard} label="Dashboard" exact />
        {moduleInfo && selectedModule && (
          <NavItem
            to={moduleInfo.ruta}
            icon={({ className }: { className?: string }) => (
              <ModuleIcon id={selectedModule as ModuleId} className={className} />
            )}
            label={moduleInfo.nombre}
          />
        )}
        <NavItem to="/app/perfil" icon={UserRound} label="Mi perfil" exact />
        {isAdmin && <NavItem to="/app/usuarios" icon={UsersRound} label="Usuarios" exact />}

        <div className="pt-3">
          <button
            type="button"
            onClick={cambiarModulo}
            className="flex h-10 w-full items-center gap-2.5 rounded-control px-3 text-sm font-semibold text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
          >
            <ArrowLeftRight className="size-4" />
            Cambiar módulo
          </button>
        </div>

        {selectedModule === 'guion' && status === 'live' && (
          <Link
            to={`/app/guion/${activeGuionId ?? 1}/en-vivo`}
            className="mt-4 block rounded-card border border-live/20 bg-live-soft p-3 transition-colors hover:border-live/40"
          >
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-[0.14em] text-live">
                <span className="size-1.5 rounded-full bg-live live-dot" />
                En vivo
              </span>
              <Radio className="size-3.5 text-live" />
            </div>
            <p className="tabular mt-2 font-mono text-lg font-bold text-ink">{formatElapsed(elapsed)}</p>
            <p className="mt-0.5 text-[10px] text-ink-muted">Abrir control del show</p>
          </Link>
        )}
      </nav>

      <div className="border-t border-line p-4">
        <div className="flex items-center gap-2.5">
          <Avatar name={user.nombre} size="sm" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold text-ink">{user.nombre}</p>
            <p className="truncate text-[10px] text-ink-muted">
              {user.rol} · {user.departamento}
            </p>
          </div>
          <button
            type="button"
            onClick={cerrarSesion}
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
            className="grid size-8 place-items-center rounded-md text-ink-muted transition-colors hover:bg-danger-soft hover:text-danger"
          >
            <LogOut className="size-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}

import { Bell, Search } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { Logo } from '@/components/brand/Logo'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { UserMenu } from '@/components/layout/UserMenu'
import { Kbd } from '@/components/ui/Kbd'
import { useData } from '@/hooks/useData'

const TITULOS: Record<string, string> = {
  '/app/dashboard': 'Dashboard',
  '/app/patrocinantes': 'Patrocinantes',
  '/app/balance': 'Balance',
  '/app/inventario': 'Inventario',
  '/app/tareas': 'Tareas',
  '/app/guion': 'Guion',
  '/app/guion/nuevo': 'Nuevo guion',
  '/app/perfil': 'Mi perfil',
  '/app/usuarios': 'Usuarios',
}

function tituloDeRuta(pathname: string) {
  if (TITULOS[pathname]) return TITULOS[pathname]
  if (/^\/app\/guion\/\d+\/editar$/.test(pathname)) return 'Editar guion'
  return 'Itinerario'
}

export function Topbar({
  onSearch,
  onNotifications,
}: {
  onSearch: () => void
  onNotifications: () => void
}) {
  const { pathname } = useLocation()
  const { unreadCount } = useData()
  const title = tituloDeRuta(pathname)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b border-line bg-canvas/85 px-4 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <div className="lg:hidden">
          <Logo size="sm" withWordmark={false} />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-bold text-ink">{title}</p>
          <p className="hidden text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-faint sm:block">
            Palco de Operaciones
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={onSearch}
          className="hidden h-10 items-center gap-2 rounded-control border border-line bg-surface px-3 text-xs font-medium text-ink-muted transition-colors hover:border-line-strong hover:text-ink sm:flex"
        >
          <Search className="size-4" />
          Buscar
          <Kbd className="ml-2">⌘K</Kbd>
        </button>
        <button
          type="button"
          onClick={onSearch}
          aria-label="Buscar"
          className="grid size-10 place-items-center rounded-control border border-line bg-surface text-ink-muted transition-colors hover:text-ink sm:hidden"
        >
          <Search className="size-4" />
        </button>
        <ThemeToggle />
        <button
          type="button"
          onClick={onNotifications}
          aria-label="Notificaciones"
          className="relative grid size-10 place-items-center rounded-control border border-line bg-surface text-ink-muted transition-colors hover:text-ink"
        >
          <Bell className="size-4" />
          {unreadCount > 0 && (
            <span className="absolute right-1.5 top-1.5 grid min-w-4 place-items-center rounded-full bg-brand px-1 text-[9px] font-bold leading-4 text-white">
              {unreadCount}
            </span>
          )}
        </button>
        <div className="ml-1">
          <UserMenu />
        </div>
      </div>
    </header>
  )
}

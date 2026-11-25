import { LayoutDashboard, UserRound } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { useSession } from '@/hooks/useSession'
import { MODULO_POR_ID } from '@/lib/constants'
import { cn } from '@/lib/cn'
import type { ModuleId } from '@/types'

export function MobileNav() {
  const { selectedModule } = useSession()
  const moduleInfo = selectedModule ? MODULO_POR_ID[selectedModule] : null

  const items = [
    { to: '/app/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="size-5" />, end: true },
    ...(moduleInfo && selectedModule
      ? [
          {
            to: moduleInfo.ruta,
            label: moduleInfo.nombre,
            icon: <ModuleIcon id={selectedModule as ModuleId} className="size-5" />,
            end: false,
          },
        ]
      : []),
    { to: '/app/perfil', label: 'Perfil', icon: <UserRound className="size-5" />, end: true },
  ]

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-canvas/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-md lg:hidden">
      <div className="mx-auto grid max-w-md grid-cols-3">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cn(
                'flex min-h-14 flex-col items-center justify-center gap-1 text-[10px] font-semibold transition-colors',
                isActive ? 'text-brand' : 'text-ink-muted hover:text-ink',
              )
            }
          >
            {item.icon}
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}

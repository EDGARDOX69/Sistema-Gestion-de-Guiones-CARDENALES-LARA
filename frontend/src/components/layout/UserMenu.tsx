import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { ChevronDown, LogOut, ShieldCheck, UserRound, UsersRound, ArrowLeftRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Avatar } from '@/components/ui/Avatar'
import { useSession } from '@/hooks/useSession'

const itemClass =
  'flex cursor-pointer select-none items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-ink-soft outline-none data-[highlighted]:bg-brand-soft data-[highlighted]:text-brand'

export function UserMenu() {
  const { user, isAdmin, clearModule, logout } = useSession()
  const navigate = useNavigate()

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
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          aria-label="Menú de usuario"
          className="flex items-center gap-2 rounded-control border border-transparent p-1 pr-2 transition-colors hover:border-line hover:bg-surface data-[state=open]:border-line data-[state=open]:bg-surface"
        >
          <Avatar name={user.nombre} size="sm" />
          <span className="hidden text-left sm:block">
            <span className="block max-w-32 truncate text-xs font-semibold text-ink">{user.nombre}</span>
            <span className="block text-[10px] text-ink-muted">{user.rol}</span>
          </span>
          <ChevronDown className="hidden size-3.5 text-ink-muted sm:block" />
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={8}
          className="z-[70] min-w-64 rounded-card border border-line bg-raised p-1.5 text-ink shadow-pop"
        >
          <DropdownMenu.Label className="px-2.5 py-2">
            <span className="block text-sm font-bold text-ink">{user.nombre}</span>
            <span className="mt-0.5 block truncate text-[11px] text-ink-muted">{user.email}</span>
            <span className="mt-1.5 inline-flex items-center gap-1 rounded-full bg-brand-soft px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-brand">
              <ShieldCheck className="size-3" />
              {user.rol}
            </span>
          </DropdownMenu.Label>
          <DropdownMenu.Separator className="my-1 h-px bg-line" />
          <DropdownMenu.Item className={itemClass} onSelect={() => navigate('/app/perfil')}>
            <UserRound className="size-4" />
            Mi perfil
          </DropdownMenu.Item>
          {isAdmin && (
            <DropdownMenu.Item className={itemClass} onSelect={() => navigate('/app/usuarios')}>
              <UsersRound className="size-4" />
              Usuarios del sistema
            </DropdownMenu.Item>
          )}
          <DropdownMenu.Item className={itemClass} onSelect={cambiarModulo}>
            <ArrowLeftRight className="size-4" />
            Cambiar módulo
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="my-1 h-px bg-line" />
          <DropdownMenu.Item
            className="flex cursor-pointer select-none items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-danger outline-none data-[highlighted]:bg-danger-soft"
            onSelect={cerrarSesion}
          >
            <LogOut className="size-4" />
            Cerrar sesión
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}

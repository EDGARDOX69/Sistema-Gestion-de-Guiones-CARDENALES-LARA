import * as DialogPrimitive from '@radix-ui/react-dialog'
import { Command } from 'cmdk'
import {
  ArrowLeftRight,
  LayoutDashboard,
  LogOut,
  Moon,
  Plus,
  Radio,
  Search,
  Sun,
  UserRound,
  UsersRound,
} from 'lucide-react'
import type { ComponentType } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { Kbd } from '@/components/ui/Kbd'
import { useLiveShow } from '@/hooks/useLiveShow'
import { useSession } from '@/hooks/useSession'
import { useTheme } from '@/hooks/useTheme'
import { MODULO_POR_ID } from '@/lib/constants'
import type { ModuleId } from '@/types'

function Item({
  icon: Icon,
  label,
  value,
  onSelect,
}: {
  icon: ComponentType<{ className?: string }>
  label: string
  value: string
  onSelect: () => void
}) {
  return (
    <Command.Item
      value={value}
      onSelect={onSelect}
      className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-sm text-ink-soft outline-none data-[selected=true]:bg-brand-soft data-[selected=true]:text-brand"
    >
      <Icon className="size-4" />
      {label}
    </Command.Item>
  )
}

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const navigate = useNavigate()
  const { selectedModule, isAdmin, clearModule, logout } = useSession()
  const { activeGuionId, status } = useLiveShow()
  const { resolvedTheme, toggleTheme } = useTheme()
  const info = selectedModule ? MODULO_POR_ID[selectedModule] : null

  const run = (action: () => void) => {
    onOpenChange(false)
    action()
  }

  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="dialog-overlay fixed inset-0 z-[60] bg-night-950/60 backdrop-blur-[2px]" />
        <div className="fixed inset-0 z-[60] flex items-start justify-center p-4 pt-[12vh]">
          <DialogPrimitive.Content className="dialog-content w-full max-w-xl overflow-hidden rounded-card border border-line bg-surface text-ink shadow-pop">
            <DialogPrimitive.Title className="sr-only">Comandos</DialogPrimitive.Title>
            <DialogPrimitive.Description className="sr-only">
              Busca páginas, módulos y acciones del sistema.
            </DialogPrimitive.Description>
            <Command
              loop
              className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-[10px] [&_[cmdk-group-heading]]:font-bold [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-[0.14em] [&_[cmdk-group-heading]]:text-ink-muted"
            >
              <div className="flex items-center gap-2 border-b border-line px-4">
                <Search className="size-4 text-ink-muted" />
                <Command.Input
                  autoFocus
                  placeholder="Buscar páginas, módulos o acciones..."
                  className="h-12 w-full bg-transparent text-sm text-ink outline-none placeholder:text-ink-faint"
                />
                <Kbd>ESC</Kbd>
              </div>
              <Command.List className="scroll-area max-h-[58vh] overflow-y-auto p-2">
                <Command.Empty className="px-3 py-10 text-center text-sm text-ink-muted">
                  Sin resultados.
                </Command.Empty>
                <Command.Group heading="Navegación">
                  <Item
                    icon={LayoutDashboard}
                    label="Ir al dashboard"
                    value="dashboard"
                    onSelect={() => run(() => navigate('/app/dashboard'))}
                  />
                  {selectedModule && info && (
                    <Item
                      icon={({ className }: { className?: string }) => (
                        <ModuleIcon id={selectedModule as ModuleId} className={className} />
                      )}
                      label={`Ir a ${info.nombre}`}
                      value={`modulo-${info.id}`}
                      onSelect={() => run(() => navigate(info.ruta))}
                    />
                  )}
                  {selectedModule === 'guion' && status === 'live' && (
                    <Item
                      icon={Radio}
                      label="Abrir control en vivo"
                      value="control-en-vivo"
                      onSelect={() => run(() => navigate(`/app/guion/${activeGuionId ?? 1}/en-vivo`))}
                    />
                  )}
                  <Item
                    icon={UserRound}
                    label="Mi perfil"
                    value="perfil"
                    onSelect={() => run(() => navigate('/app/perfil'))}
                  />
                  {isAdmin && (
                    <Item
                      icon={UsersRound}
                      label="Usuarios del sistema"
                      value="usuarios"
                      onSelect={() => run(() => navigate('/app/usuarios'))}
                    />
                  )}
                </Command.Group>

                {selectedModule && (
                  <Command.Group heading="Acciones del módulo">
                    {selectedModule === 'patrocinantes' && (
                      <Item
                        icon={Plus}
                        label="Nuevo patrocinante"
                        value="nuevo-patrocinante"
                        onSelect={() => run(() => navigate('/app/patrocinantes?nuevo=1'))}
                      />
                    )}
                    {selectedModule === 'balance' && (
                      <Item
                        icon={Plus}
                        label="Registrar pago"
                        value="registrar-pago"
                        onSelect={() => run(() => navigate('/app/balance?pago=1'))}
                      />
                    )}
                    {selectedModule === 'inventario' && (
                      <Item
                        icon={Plus}
                        label="Nuevo recurso"
                        value="nuevo-recurso"
                        onSelect={() => run(() => navigate('/app/inventario?nuevo=1'))}
                      />
                    )}
                    {selectedModule === 'tareas' && (
                      <Item
                        icon={Plus}
                        label="Nueva tarea"
                        value="nueva-tarea"
                        onSelect={() => run(() => navigate('/app/tareas?nueva=1'))}
                      />
                    )}
                    {selectedModule === 'guion' && (
                      <Item
                        icon={Plus}
                        label="Nuevo guion"
                        value="nuevo-guion"
                        onSelect={() => run(() => navigate('/app/guion/nuevo'))}
                      />
                    )}
                  </Command.Group>
                )}

                <Command.Group heading="Sesión">
                  <Item
                    icon={ArrowLeftRight}
                    label="Cambiar módulo"
                    value="cambiar-modulo"
                    onSelect={() =>
                      run(() => {
                        clearModule()
                        navigate('/modulos')
                      })
                    }
                  />
                  <Item
                    icon={resolvedTheme === 'dark' ? Sun : Moon}
                    label={resolvedTheme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
                    value="cambiar-tema"
                    onSelect={() => run(toggleTheme)}
                  />
                  <Item
                    icon={LogOut}
                    label="Cerrar sesión"
                    value="cerrar-sesion"
                    onSelect={() =>
                      run(() => {
                        logout()
                        navigate('/login')
                        toast.success('Sesión cerrada')
                      })
                    }
                  />
                </Command.Group>
              </Command.List>
            </Command>
          </DialogPrimitive.Content>
        </div>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}

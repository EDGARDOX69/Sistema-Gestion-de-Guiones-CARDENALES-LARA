import { zodResolver } from '@hookform/resolvers/zod'
import {
  ArrowLeftRight,
  Bell,
  CheckCircle2,
  Clock,
  KeyRound,
  Laptop,
  MapPin,
  Monitor,
  Moon,
  Palette,
  RefreshCw,
  ShieldCheck,
  Sun,
  UserRound,
  UsersRound,
} from 'lucide-react'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { ModuleIcon } from '@/components/brand/ModuleIcon'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Input, PasswordInput } from '@/components/ui/Input'
import { PageHeader } from '@/components/ui/PageHeader'
import { SegmentedControl } from '@/components/ui/SegmentedControl'
import { Select } from '@/components/ui/Select'
import { Switch } from '@/components/ui/Switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { useData } from '@/hooks/useData'
import { useSession } from '@/hooks/useSession'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/cn'
import { DEPARTAMENTOS, MODULO_POR_ID, MODULE_ACCENT } from '@/lib/constants'
import { formatDate } from '@/lib/format'
import {
  passwordChangeSchema,
  perfilSchema,
  type PasswordChangeForm,
  type PerfilForm,
} from '@/lib/schemas'
import type { ModuleId } from '@/types'

const PERMISOS: Record<ModuleId, string[]> = {
  patrocinantes: ['patrocinador.view', 'patrocinador.create', 'patrocinador.edit', 'patrocinador.delete'],
  balance: ['balance.view', 'balance.create', 'balance.edit', 'balance.delete'],
  inventario: ['inventario.view', 'inventario.create', 'inventario.edit', 'inventario.asignar'],
  tareas: ['tarea.view', 'tarea.create', 'tarea.edit', 'tarea.asignar'],
  guion: ['guion.view', 'guion.create', 'guion.edit', 'guion.publish', 'envivo.view', 'envivo.control'],
}

const PASSWORD_LEVELS = ['Muy débil', 'Débil', 'Aceptable', 'Fuerte', 'Excelente']

export function PerfilPage() {
  const navigate = useNavigate()
  const { user, selectedModule, clearModule, updateUser, isAdmin } = useSession()
  const { theme, setTheme } = useTheme()
  const { resetDemo } = useData()
  const [notificacionesTarea, setNotificacionesTarea] = useState(true)
  const [notificacionesPago, setNotificacionesPago] = useState(true)
  const [sonido, setSonido] = useState(false)
  const [resetOpen, setResetOpen] = useState(false)

  const moduleInfo = selectedModule ? MODULO_POR_ID[selectedModule] : null
  const accent = selectedModule ? MODULE_ACCENT[selectedModule] : null

  const datosForm = useForm<PerfilForm>({
    resolver: zodResolver(perfilSchema),
    defaultValues: {
      nombre: user?.nombre ?? '',
      email: user?.email ?? '',
      telefono: user?.telefono ?? '',
      cedula: user?.cedula ?? '',
      departamento: user?.departamento ?? 'Medios',
    },
  })

  const passwordForm = useForm<PasswordChangeForm>({
    resolver: zodResolver(passwordChangeSchema),
    defaultValues: { actual: '', nueva: '', confirmar: '' },
  })
  const nuevaPassword = passwordForm.watch('nueva')
  const score = [
    nuevaPassword.length >= 8,
    /[A-Z]/.test(nuevaPassword),
    /[a-z]/.test(nuevaPassword),
    /[0-9]/.test(nuevaPassword),
  ].filter(Boolean).length

  if (!user) return null

  const guardarDatos = (values: PerfilForm) => {
    updateUser(values)
    datosForm.reset(values)
    toast.success('Datos actualizados')
  }

  const cambiarPassword = () => {
    toast.success('Contraseña actualizada', { description: 'Las sesiones anteriores quedaron cerradas.' })
    passwordForm.reset()
  }

  const cambiarModulo = () => {
    clearModule()
    navigate('/modulos')
  }

  const confirmarReset = () => {
    resetDemo()
    toast.success('Datos de demostración restablecidos')
    setResetOpen(false)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Cuenta y acceso"
        title="Mi perfil"
        description="Datos personales, seguridad y preferencias de la sesión."
        actions={
          <Button variant="secondary" size="sm" onClick={cambiarModulo} leftIcon={<ArrowLeftRight className="size-3.5" />}>
            Cambiar módulo
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="space-y-4 lg:col-span-4">
          <Card className="overflow-hidden">
            <div className="h-20 bg-gradient-to-br from-brand/25 via-brand/10 to-time/15" />
            <div className="-mt-8 px-5 pb-5">
              <Avatar name={user.nombre} size="lg" className="size-16 border-4 border-surface text-lg" />
              <p className="mt-3 text-lg font-bold text-ink">{user.nombre}</p>
              <p className="text-xs text-ink-muted">{user.email}</p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                <Badge tone="brand" size="sm">
                  <ShieldCheck className="size-3" />
                  {user.rol}
                </Badge>
                <Badge tone="neutral" size="sm">{user.departamento}</Badge>
              </div>
              <div className="mt-4 space-y-2 border-t border-line pt-4 text-xs">
                <div className="flex items-center gap-2 text-ink-muted">
                  <UserRound className="size-3.5" />
                  <span className="text-ink-soft">Cédula</span>
                  <span className="ml-auto font-semibold text-ink">{user.cedula}</span>
                </div>
                <div className="flex items-center gap-2 text-ink-muted">
                  <Clock className="size-3.5" />
                  <span className="text-ink-soft">Último acceso</span>
                  <span className="ml-auto font-semibold text-ink">{formatDate(user.ultimoAcceso)}</span>
                </div>
                <div className="flex items-center gap-2 text-ink-muted">
                  <Laptop className="size-3.5" />
                  <span className="text-ink-soft">Sesión</span>
                  <span className="ml-auto font-semibold text-ink">Chrome · Windows</span>
                </div>
                <div className="flex items-center gap-2 text-ink-muted">
                  <MapPin className="size-3.5" />
                  <span className="text-ink-soft">Ubicación</span>
                  <span className="ml-auto font-semibold text-ink">Barquisimeto</span>
                </div>
              </div>
            </div>
          </Card>

          {moduleInfo && accent && (
            <Card className="p-4">
              <p className="eyebrow">Módulo activo</p>
              <div className={cn('mt-2 flex items-center gap-2.5 rounded-control border p-3', accent.border, accent.bg)}>
                <span className={cn('grid size-9 place-items-center rounded-control bg-surface', accent.text)}>
                  <ModuleIcon id={selectedModule as ModuleId} className="size-4" />
                </span>
                <div className="min-w-0">
                  <p className="truncate text-sm font-bold text-ink">{moduleInfo.nombre}</p>
                  <p className="truncate text-[10px] text-ink-muted">Sesión enfocada</p>
                </div>
              </div>
              <Button variant="secondary" className="mt-3 w-full" onClick={cambiarModulo} leftIcon={<ArrowLeftRight className="size-4" />}>
                Cambiar módulo
              </Button>
            </Card>
          )}

          {isAdmin && (
            <Card className="p-4">
              <p className="eyebrow">Administración</p>
              <p className="mt-1 text-xs text-ink-muted">Gestiona los usuarios y sus roles en el sistema.</p>
              <Button variant="secondary" className="mt-3 w-full" onClick={() => navigate('/app/usuarios')} leftIcon={<UsersRound className="size-4" />}>
                Usuarios del sistema
              </Button>
            </Card>
          )}
        </div>

        <Card className="p-5 lg:col-span-8">
          <Tabs defaultValue="datos">
            <TabsList>
              <TabsTrigger value="datos">Datos personales</TabsTrigger>
              <TabsTrigger value="seguridad">Seguridad</TabsTrigger>
              <TabsTrigger value="preferencias">Preferencias</TabsTrigger>
              <TabsTrigger value="permisos">Permisos</TabsTrigger>
            </TabsList>

            <TabsContent value="datos">
              <form onSubmit={datosForm.handleSubmit(guardarDatos)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
                <Input label="Nombre completo" error={datosForm.formState.errors.nombre?.message} {...datosForm.register('nombre')} />
                <Input label="Correo electrónico" type="email" error={datosForm.formState.errors.email?.message} {...datosForm.register('email')} />
                <Input label="Teléfono" error={datosForm.formState.errors.telefono?.message} {...datosForm.register('telefono')} />
                <Input label="Cédula" error={datosForm.formState.errors.cedula?.message} {...datosForm.register('cedula')} />
                <Controller
                  control={datosForm.control}
                  name="departamento"
                  render={({ field }) => (
                    <Select
                      label="Departamento"
                      options={DEPARTAMENTOS.map((departamento) => ({ value: departamento, label: departamento }))}
                      value={field.value}
                      onValueChange={field.onChange}
                      error={datosForm.formState.errors.departamento?.message}
                      className="sm:col-span-2"
                    />
                  )}
                />
                <div className="sm:col-span-2">
                  <Button type="submit" loading={datosForm.formState.isSubmitting}>Guardar cambios</Button>
                </div>
              </form>
            </TabsContent>

            <TabsContent value="seguridad">
              <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                <form onSubmit={passwordForm.handleSubmit(cambiarPassword)} className="space-y-4" noValidate>
                  <div className="flex items-center gap-2">
                    <KeyRound className="size-4 text-brand" />
                    <p className="text-sm font-bold text-ink">Cambiar contraseña</p>
                  </div>
                  <PasswordInput label="Contraseña actual" autoComplete="current-password" error={passwordForm.formState.errors.actual?.message} {...passwordForm.register('actual')} />
                  <PasswordInput label="Nueva contraseña" autoComplete="new-password" error={passwordForm.formState.errors.nueva?.message} {...passwordForm.register('nueva')} />
                  <div>
                    <div className="flex gap-1.5">
                      {Array.from({ length: 4 }, (_, index) => (
                        <span key={index} className={cn('h-1.5 flex-1 rounded-full', index < score ? (score >= 4 ? 'bg-live' : score >= 3 ? 'bg-info' : 'bg-time') : 'bg-sunken')} />
                      ))}
                    </div>
                    <p className="mt-1 text-[10px] text-ink-muted">{PASSWORD_LEVELS[score]}</p>
                  </div>
                  <PasswordInput label="Confirmar contraseña" autoComplete="new-password" error={passwordForm.formState.errors.confirmar?.message} {...passwordForm.register('confirmar')} />
                  <Button type="submit" variant="secondary">Actualizar contraseña</Button>
                </form>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Monitor className="size-4 text-info" />
                    <p className="text-sm font-bold text-ink">Sesión actual</p>
                  </div>
                  <div className="rounded-control border border-line bg-sunken/35 p-3">
                    <div className="flex items-center gap-2">
                      <span className="grid size-8 place-items-center rounded-control bg-surface text-info">
                        <Laptop className="size-4" />
                      </span>
                      <div>
                        <p className="text-xs font-semibold text-ink">Chrome en Windows</p>
                        <p className="text-[10px] text-ink-muted">Sesión iniciada · Barquisimeto, VE</p>
                      </div>
                      <Badge tone="live" size="sm" className="ml-auto">Activa</Badge>
                    </div>
                  </div>
                  <Button variant="ghost" onClick={() => toast.success('Las otras sesiones fueron cerradas')}>
                    Cerrar las otras sesiones
                  </Button>
                  <div className="rounded-control border border-live/20 bg-live-soft p-3 text-[11px] text-live">
                    <p className="flex items-center gap-1.5 font-bold"><CheckCircle2 className="size-3.5" /> Protección activa</p>
                    <p className="mt-1 text-live/80">Sesión única y contraseña cifrada en el servidor.</p>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="preferencias">
              <div className="space-y-6">
                <div>
                  <div className="flex items-center gap-2">
                    <Palette className="size-4 text-brand" />
                    <p className="text-sm font-bold text-ink">Apariencia</p>
                  </div>
                  <p className="mt-0.5 text-xs text-ink-muted">Elige cómo se ve el palco en este dispositivo.</p>
                  <SegmentedControl
                    className="mt-3"
                    value={theme}
                    onValueChange={(value) => setTheme(value as 'light' | 'dark' | 'system')}
                    ariaLabel="Tema de la interfaz"
                    options={[
                      { value: 'light', label: 'Claro', icon: Sun },
                      { value: 'dark', label: 'Oscuro', icon: Moon },
                      { value: 'system', label: 'Sistema', icon: Monitor },
                    ]}
                  />
                </div>

                <div className="space-y-4 border-t border-line pt-5">
                  <div className="flex items-center gap-2">
                    <Bell className="size-4 text-time" />
                    <p className="text-sm font-bold text-ink">Notificaciones</p>
                  </div>
                  <Switch checked={notificacionesTarea} onCheckedChange={setNotificacionesTarea} label="Tareas asignadas" description="Avisar cuando te asignen una tarea." />
                  <Switch checked={notificacionesPago} onCheckedChange={setNotificacionesPago} label="Pagos y guiones" description="Avisar sobre movimientos de balance y publicaciones." />
                  <Switch checked={sonido} onCheckedChange={setSonido} label="Sonido" description="Reproducir un aviso al recibir notificaciones." />
                </div>

                <div className="border-t border-line pt-5">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="size-4 text-info" />
                    <p className="text-sm font-bold text-ink">Datos de demostración</p>
                  </div>
                  <p className="mt-0.5 text-xs text-ink-muted">Restablece patrocinantes, pagos, tareas y guiones a su estado inicial.</p>
                  <Button variant="secondary" className="mt-3" onClick={() => setResetOpen(true)} leftIcon={<RefreshCw className="size-4" />}>
                    Restablecer datos
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="permisos">
              {moduleInfo && selectedModule ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="size-4 text-live" />
                    <p className="text-sm font-bold text-ink">Permisos del módulo activo</p>
                  </div>
                  <div className="rounded-control border border-line bg-sunken/35 p-3">
                    <p className="text-xs font-semibold text-ink">{moduleInfo.nombre}</p>
                    <p className="text-[10px] text-ink-muted">Los permisos se validan en el servidor para cada acción.</p>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {PERMISOS[selectedModule].map((permiso) => (
                      <Badge key={permiso} tone="info" size="sm">{permiso}</Badge>
                    ))}
                  </div>
                  <div className="rounded-control border border-live/20 bg-live-soft p-3 text-[11px] text-live">
                    <p className="flex items-center gap-1.5 font-bold"><CheckCircle2 className="size-3.5" /> Acceso verificado</p>
                    <p className="mt-1 text-live/80">Tu rol actual es {user.rol} y la sesión está activa.</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-ink-muted">Selecciona un módulo para ver sus permisos.</p>
              )}
            </TabsContent>
          </Tabs>
        </Card>
      </div>

      <ConfirmDialog
        open={resetOpen}
        onOpenChange={setResetOpen}
        title="Restablecer datos"
        description="Se restaurarán los datos de demostración. Los cambios que hayas hecho en esta sesión se perderán."
        confirmLabel="Restablecer"
        onConfirm={confirmarReset}
      />
    </div>
  )
}

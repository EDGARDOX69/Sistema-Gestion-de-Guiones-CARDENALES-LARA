import { zodResolver } from '@hookform/resolvers/zod'
import {
  Building2,
  Eye,
  KeyRound,
  Mail,
  Pencil,
  Phone,
  ShieldCheck,
  Trash2,
  UserPlus,
  UsersRound,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Avatar } from '@/components/ui/Avatar'
import { Badge, type Tone } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Drawer } from '@/components/ui/Drawer'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input, PasswordInput } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { ScoreboardStrip } from '@/components/ui/ScoreboardStrip'
import { SearchInput } from '@/components/ui/SearchInput'
import { Select } from '@/components/ui/Select'
import { Switch } from '@/components/ui/Switch'
import { useData } from '@/hooks/useData'
import { useSession } from '@/hooks/useSession'
import { DEPARTAMENTOS, ROLES } from '@/lib/constants'
import { formatDate } from '@/lib/format'
import { usuarioSchema, type UsuarioForm } from '@/lib/schemas'
import type { Usuario } from '@/types'

const ROL_TONE: Record<string, Tone> = {
  Superadmin: 'brand',
  Administrador: 'info',
  Usuario: 'neutral',
}

const PERMISOS_ROL: Record<string, string[]> = {
  Superadmin: [
    'dashboard.view',
    'usuario.view',
    'usuario.create',
    'usuario.edit',
    'usuario.delete',
    'guion.view',
    'envivo.control',
    'patrocinador.view',
    'balance.view',
    'inventario.view',
    'tarea.view',
    'reportes.view',
  ],
  Administrador: [
    'dashboard.view',
    'guion.view',
    'envivo.view',
    'patrocinador.view',
    'balance.view',
    'balance.create',
    'inventario.view',
    'tarea.view',
    'tarea.asignar',
    'reportes.view',
  ],
  Usuario: ['dashboard.view', 'guion.view', 'tarea.view', 'inventario.view'],
}

function UsuarioFormModal({
  open,
  onOpenChange,
  usuario,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  usuario: Usuario | null
}) {
  const { saveUsuario } = useData()
  const [activo, setActivo] = useState(usuario?.activo ?? true)
  const form = useForm<UsuarioForm>({
    resolver: zodResolver(usuarioSchema),
    defaultValues: {
      nombre: usuario?.nombre ?? '',
      email: usuario?.email ?? '',
      cedula: usuario?.cedula ?? '',
      telefono: usuario?.telefono ?? '',
      rol: usuario?.rol ?? 'Usuario',
      departamento: usuario?.departamento ?? 'Medios',
      password: '',
    },
  })

  const onSubmit = (values: UsuarioForm) => {
    if (!usuario && values.password.length < 8) {
      form.setError('password', { message: 'La contraseña temporal debe tener al menos 8 caracteres' })
      return
    }
    saveUsuario(
      {
        nombre: values.nombre,
        email: values.email,
        cedula: values.cedula,
        telefono: values.telefono,
        rol: values.rol,
        departamento: values.departamento,
        activo,
      },
      usuario?.id,
    )
    toast.success(usuario ? 'Usuario actualizado' : 'Usuario registrado')
    onOpenChange(false)
  }

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={usuario ? 'Editar usuario' : 'Nuevo usuario'}
      description="Cuenta, rol y departamento dentro del palco."
      icon={UserPlus}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>
            {usuario ? 'Guardar cambios' : 'Registrar usuario'}
          </Button>
        </>
      }
    >
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-2" noValidate>
        <Input label="Nombre completo" error={form.formState.errors.nombre?.message} className="sm:col-span-2" {...form.register('nombre')} />
        <Input label="Correo electrónico" type="email" error={form.formState.errors.email?.message} {...form.register('email')} />
        <Input label="Cédula" error={form.formState.errors.cedula?.message} {...form.register('cedula')} />
        <Input label="Teléfono" error={form.formState.errors.telefono?.message} {...form.register('telefono')} />
        <Controller
          control={form.control}
          name="departamento"
          render={({ field }) => (
            <Select
              label="Departamento"
              options={DEPARTAMENTOS.map((departamento) => ({ value: departamento, label: departamento }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.departamento?.message}
            />
          )}
        />
        <Controller
          control={form.control}
          name="rol"
          render={({ field }) => (
            <Select
              label="Rol"
              options={ROLES.map((rol) => ({ value: rol, label: rol }))}
              value={field.value}
              onValueChange={field.onChange}
              error={form.formState.errors.rol?.message}
              className="sm:col-span-2"
            />
          )}
        />
        {!usuario && (
          <PasswordInput
            label="Contraseña temporal"
            autoComplete="new-password"
            placeholder="Mínimo 8 caracteres"
            error={form.formState.errors.password?.message}
            className="sm:col-span-2"
            {...form.register('password')}
          />
        )}
        <div className="rounded-control border border-line bg-sunken/35 p-3 sm:col-span-2">
          <Switch checked={activo} onCheckedChange={setActivo} label="Usuario activo" description="Puede iniciar sesión y recibir notificaciones." />
        </div>
      </form>
    </Modal>
  )
}

export function UsuariosPage() {
  const { usuarios, deleteUsuario } = useData()
  const { user, isAdmin } = useSession()
  const [search, setSearch] = useState('')
  const [rolFilter, setRolFilter] = useState('all')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Usuario | null>(null)
  const [selected, setSelected] = useState<Usuario | null>(null)
  const [toDelete, setToDelete] = useState<Usuario | null>(null)

  const filtrados = useMemo(() => {
    const term = search.trim().toLowerCase()
    return usuarios.filter((usuario) => {
      const coincideTexto = !term || usuario.nombre.toLowerCase().includes(term) || usuario.email.toLowerCase().includes(term)
      const coincideRol = rolFilter === 'all' || usuario.rol === rolFilter
      return coincideTexto && coincideRol
    })
  }, [usuarios, search, rolFilter])

  const activos = usuarios.filter((usuario) => usuario.activo).length
  const admins = usuarios.filter((usuario) => usuario.rol !== 'Usuario').length
  const departamentos = new Set(usuarios.map((usuario) => usuario.departamento)).size

  if (!isAdmin) {
    return (
      <EmptyState
        icon={ShieldCheck}
        title="Acceso restringido"
        description="Solo los administradores pueden gestionar los usuarios del sistema."
      />
    )
  }

  const abrirNuevo = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const abrirEditar = (usuario: Usuario) => {
    setSelected(null)
    setEditing(usuario)
    setModalOpen(true)
  }

  const confirmarEliminar = () => {
    if (!toDelete) return
    if (toDelete.id === user?.id) {
      toast.error('No puedes eliminar tu propio usuario')
      setToDelete(null)
      return
    }
    deleteUsuario(toDelete.id)
    toast.success('Usuario eliminado')
    setToDelete(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administración"
        title="Usuarios"
        description="Cuentas, roles y departamentos del equipo."
        actions={<Button size="sm" leftIcon={<UserPlus className="size-3.5" />} onClick={abrirNuevo}>Nuevo usuario</Button>}
      />

      <ScoreboardStrip
        items={[
          { label: 'Usuarios', value: String(usuarios.length), hint: 'En el sistema', tone: 'info', icon: UsersRound },
          { label: 'Activos', value: String(activos), hint: 'Con acceso al palco', tone: 'live', icon: ShieldCheck },
          { label: 'Administradores', value: String(admins), hint: 'Superadmin y admin', tone: 'brand', icon: KeyRound },
          { label: 'Departamentos', value: String(departamentos), hint: 'Áreas conectadas', tone: 'time', icon: Building2 },
        ]}
      />

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-line p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-bold text-ink">Equipo del palco</p>
            <p className="text-[11px] text-ink-muted">{filtrados.length} de {usuarios.length} usuarios</p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <SearchInput value={search} onChange={setSearch} placeholder="Buscar nombre o correo" className="sm:w-64" />
            <Select
              options={[{ value: 'all', label: 'Todos los roles' }, ...ROLES.map((rol) => ({ value: rol, label: rol }))]}
              value={rolFilter}
              onValueChange={setRolFilter}
              className="sm:w-44"
            />
          </div>
        </div>

        {filtrados.length === 0 ? (
          <div className="p-6">
            <EmptyState icon={UsersRound} title="Sin usuarios" description="No hay usuarios que coincidan con la búsqueda." />
          </div>
        ) : (
          <>
            <div className="hidden overflow-x-auto md:block">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Departamento</th>
                    <th>Teléfono</th>
                    <th>Estado</th>
                    <th>Último acceso</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filtrados.map((usuario) => (
                    <tr key={usuario.id}>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <Avatar name={usuario.nombre} size="sm" />
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-ink">{usuario.nombre}</p>
                            <p className="truncate text-[11px] text-ink-muted">{usuario.email}</p>
                          </div>
                        </div>
                      </td>
                      <td><Badge tone={ROL_TONE[usuario.rol] ?? 'neutral'} size="sm">{usuario.rol}</Badge></td>
                      <td className="text-xs text-ink-soft">{usuario.departamento}</td>
                      <td className="text-xs text-ink-muted">{usuario.telefono}</td>
                      <td><Badge tone={usuario.activo ? 'live' : 'neutral'} size="sm" dot>{usuario.activo ? 'Activo' : 'Inactivo'}</Badge></td>
                      <td className="text-xs text-ink-muted">{formatDate(usuario.ultimoAcceso)}</td>
                      <td>
                        <div className="flex items-center justify-end gap-1">
                          <Button variant="ghost" size="icon" aria-label="Ver permisos" onClick={() => setSelected(usuario)}><Eye className="size-4" /></Button>
                          <Button variant="ghost" size="icon" aria-label="Editar usuario" onClick={() => abrirEditar(usuario)}><Pencil className="size-4" /></Button>
                          <Button variant="ghost" size="icon" aria-label="Eliminar usuario" onClick={() => setToDelete(usuario)}><Trash2 className="size-4 text-danger" /></Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="divide-y divide-line md:hidden">
              {filtrados.map((usuario) => (
                <div key={usuario.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <Avatar name={usuario.nombre} size="md" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-bold text-ink">{usuario.nombre}</p>
                      <p className="truncate text-[11px] text-ink-muted">{usuario.email}</p>
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        <Badge tone={ROL_TONE[usuario.rol] ?? 'neutral'} size="sm">{usuario.rol}</Badge>
                        <Badge tone={usuario.activo ? 'live' : 'neutral'} size="sm">{usuario.activo ? 'Activo' : 'Inactivo'}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center justify-end gap-1">
                    <Button variant="ghost" size="sm" onClick={() => setSelected(usuario)} leftIcon={<Eye className="size-3.5" />}>Ver</Button>
                    <Button variant="ghost" size="sm" onClick={() => abrirEditar(usuario)} leftIcon={<Pencil className="size-3.5" />}>Editar</Button>
                    <Button variant="ghost" size="sm" onClick={() => setToDelete(usuario)} aria-label="Eliminar usuario"><Trash2 className="size-3.5 text-danger" /></Button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>

      {modalOpen && (
        <UsuarioFormModal key={editing?.id ?? 'nuevo'} open={modalOpen} onOpenChange={setModalOpen} usuario={editing} />
      )}

      <Drawer
        open={Boolean(selected)}
        onOpenChange={(open) => !open && setSelected(null)}
        title={selected?.nombre ?? 'Usuario'}
        description={selected?.email}
        footer={
          selected && (
            <>
              <Button variant="ghost" onClick={() => setSelected(null)}>Cerrar</Button>
              <Button onClick={() => abrirEditar(selected)} leftIcon={<Pencil className="size-4" />}>Editar</Button>
            </>
          )
        }
      >
        {selected && (
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <Avatar name={selected.nombre} size="lg" />
              <div>
                <p className="text-lg font-bold text-ink">{selected.nombre}</p>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  <Badge tone={ROL_TONE[selected.rol] ?? 'neutral'} size="sm">{selected.rol}</Badge>
                  <Badge tone={selected.activo ? 'live' : 'neutral'} size="sm" dot>{selected.activo ? 'Activo' : 'Inactivo'}</Badge>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Mail className="size-3" /> Correo</p>
                <p className="mt-1 truncate text-sm font-semibold text-ink">{selected.email}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Phone className="size-3" /> Teléfono</p>
                <p className="mt-1 text-sm font-semibold text-ink">{selected.telefono}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><Building2 className="size-3" /> Departamento</p>
                <p className="mt-1 text-sm font-semibold text-ink">{selected.departamento}</p>
              </div>
              <div className="rounded-control border border-line bg-sunken/35 p-3">
                <p className="text-[10px] font-bold uppercase tracking-wide text-ink-muted">Último acceso</p>
                <p className="mt-1 text-sm font-semibold text-ink">{formatDate(selected.ultimoAcceso)}</p>
              </div>
            </div>

            <div>
              <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-ink-muted"><ShieldCheck className="size-3" /> Permisos del rol</p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {(PERMISOS_ROL[selected.rol] ?? []).map((permiso) => (
                  <Badge key={permiso} tone="info" size="sm">{permiso}</Badge>
                ))}
              </div>
            </div>
          </div>
        )}
      </Drawer>

      <ConfirmDialog
        open={Boolean(toDelete)}
        onOpenChange={(open) => !open && setToDelete(null)}
        title="Eliminar usuario"
        description={toDelete ? `Se eliminará la cuenta de "${toDelete.nombre}".` : ''}
        confirmLabel="Eliminar"
        onConfirm={confirmarEliminar}
      />
    </div>
  )
}

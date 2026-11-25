import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { PATROCINADORES, CONTRATOS, PAGOS } from '@/data/patrocinadores'
import { ASIGNACIONES, RECURSOS, TIPOS_RECURSO } from '@/data/inventario'
import { TAREAS } from '@/data/tareas'
import { GUIONES } from '@/data/guiones'
import { USUARIOS, DEMO_USER } from '@/data/usuarios'
import { ACTIVIDAD, NOTIFICACIONES } from '@/data/notificaciones'
import type {
  Actividad,
  Asignacion,
  Contrato,
  ElementoGuion,
  EstadoGuion,
  EstadoTarea,
  Guion,
  Notificacion,
  Pago,
  Patrocinador,
  Recurso,
  Tarea,
  TipoNotificacion,
  TipoRecurso,
  Usuario,
} from '@/types'

interface PatrocinadorInput {
  nombre: string
  rif: string
  tipoContrato: number
  contacto: string
  telefono: string
  email: string
  encargadoId: number
}

interface PagoInput {
  contratoId: number
  monto: number
  tipo: Pago['tipo']
  referencia: string
  fecha: string
  hora: string
  descripcion: string
}

interface RecursoInput {
  nombre: string
  descripcion: string
  tipoId: number
  estado: Recurso['estado']
  fechaCompra: string
  costo: number
}

interface TipoRecursoInput {
  nombre: string
  descripcion: string
}

interface AsignacionInput {
  recursoId: number
  usuarioId: number
  fechaDevolucionEsperada: string
  notas: string
}

interface TareaInput {
  nombre: string
  instruccion: string
  asignadoId: number
  fecha: string
  prioridad: Tarea['prioridad']
}

interface GuionInput {
  nombre: string
  fecha: string
  tiempoInning: number
  elementos: ElementoGuion[]
}

interface UsuarioInput {
  nombre: string
  email: string
  cedula: string
  telefono: string
  rol: string
  departamento: string
  activo?: boolean
}

interface DataContextValue {
  patrocinadores: Patrocinador[]
  contratos: Contrato[]
  pagos: Pago[]
  recursos: Recurso[]
  tiposRecurso: TipoRecurso[]
  asignaciones: Asignacion[]
  tareas: Tarea[]
  guiones: Guion[]
  usuarios: Usuario[]
  notificaciones: Notificacion[]
  actividad: Actividad[]
  unreadCount: number
  savePatrocinador: (input: PatrocinadorInput, id?: number) => void
  deletePatrocinador: (id: number) => void
  addPago: (input: PagoInput) => void
  updatePago: (id: number, input: PagoInput) => void
  deletePago: (id: number) => void
  saveRecurso: (input: RecursoInput, id?: number) => void
  deleteRecurso: (id: number) => void
  saveTipoRecurso: (input: TipoRecursoInput, id?: number) => void
  deleteTipoRecurso: (id: number) => { ok: boolean; error?: string }
  addAsignacion: (input: AsignacionInput) => { ok: boolean; error?: string }
  devolverAsignacion: (id: number) => void
  saveTarea: (input: TareaInput, id?: number) => void
  deleteTarea: (id: number) => void
  setTareaEstado: (id: number, estado: EstadoTarea) => void
  saveGuion: (input: GuionInput, id?: number) => number
  deleteGuion: (id: number) => void
  publicarGuion: (id: number) => void
  replicarGuion: (id: number, nombre: string, fecha: string) => number
  updateGuionEstado: (id: number, estado: EstadoGuion) => void
  saveUsuario: (input: UsuarioInput, id?: number) => void
  deleteUsuario: (id: number) => void
  notify: (tipo: TipoNotificacion, titulo: string, mensaje: string) => void
  markRead: (id: number) => void
  markAllRead: () => void
  resetDemo: () => void
}

const DataContext = createContext<DataContextValue | null>(null)

function nextId(items: { id: number }[]) {
  return items.reduce((max, item) => Math.max(max, item.id), 0) + 1
}

function nowTime() {
  return 'Ahora'
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [patrocinadores, setPatrocinadores] = useState(PATROCINADORES)
  const [contratos, setContratos] = useState(CONTRATOS)
  const [pagos, setPagos] = useState(PAGOS)
  const [recursos, setRecursos] = useState(RECURSOS)
  const [tiposRecurso, setTiposRecurso] = useState(TIPOS_RECURSO)
  const [asignaciones, setAsignaciones] = useState(ASIGNACIONES)
  const [tareas, setTareas] = useState(TAREAS)
  const [guiones, setGuiones] = useState(GUIONES)
  const [usuarios, setUsuarios] = useState(USUARIOS)
  const [notificaciones, setNotificaciones] = useState(NOTIFICACIONES)
  const [actividad, setActividad] = useState(ACTIVIDAD)

  const log = useCallback((tipo: Actividad['tipo'], titulo: string, detalle: string) => {
    setActividad((prev) => [
      {
        id: nextId(prev),
        tipo,
        titulo,
        detalle,
        tiempo: nowTime(),
        usuario: DEMO_USER.nombre,
      },
      ...prev,
    ])
  }, [])

  const notify = useCallback((tipo: TipoNotificacion, titulo: string, mensaje: string) => {
    setNotificaciones((prev) => [
      {
        id: nextId(prev),
        tipo,
        titulo,
        mensaje,
        tiempo: nowTime(),
        leida: false,
      },
      ...prev,
    ])
  }, [])

  const savePatrocinador = useCallback(
    (input: PatrocinadorInput, id?: number) => {
      if (id) {
        setPatrocinadores((prev) =>
          prev.map((item) => (item.id === id ? { ...item, ...input, tipoContrato: input.tipoContrato as Patrocinador['tipoContrato'] } : item)),
        )
        log('patrocinador', 'Patrocinante actualizado', input.nombre)
        return
      }
      setPatrocinadores((prev) => [
        ...prev,
        { id: nextId(prev), ...input, tipoContrato: input.tipoContrato as Patrocinador['tipoContrato'], estado: true },
      ])
      log('patrocinador', 'Patrocinante registrado', input.nombre)
    },
    [log],
  )

  const deletePatrocinador = useCallback(
    (id: number) => {
      const item = patrocinadores.find((patrocinador) => patrocinador.id === id)
      setPatrocinadores((prev) => prev.filter((patrocinador) => patrocinador.id !== id))
      log('patrocinador', 'Patrocinante eliminado', item?.nombre ?? `#${id}`)
    },
    [log, patrocinadores],
  )

  const addPago = useCallback(
    (input: PagoInput) => {
      setPagos((prev) => [...prev, { id: nextId(prev), registradoPor: DEMO_USER.id, ...input }])
      log('pago', 'Pago registrado', `${input.referencia} · $${input.monto}`)
      notify('pago', 'Pago registrado', `Se registró un abono de $${input.monto} en el contrato #${input.contratoId}.`)
    },
    [log, notify],
  )

  const updatePago = useCallback(
    (id: number, input: PagoInput) => {
      setPagos((prev) => prev.map((pago) => (pago.id === id ? { ...pago, ...input } : pago)))
      log('pago', 'Pago actualizado', input.referencia)
    },
    [log],
  )

  const deletePago = useCallback(
    (id: number) => {
      setPagos((prev) => prev.filter((pago) => pago.id !== id))
      log('pago', 'Pago eliminado', `Pago #${id}`)
    },
    [log],
  )

  const saveRecurso = useCallback(
    (input: RecursoInput, id?: number) => {
      if (id) {
        setRecursos((prev) => prev.map((recurso) => (recurso.id === id ? { ...recurso, ...input } : recurso)))
        log('inventario', 'Recurso actualizado', input.nombre)
        return
      }
      setRecursos((prev) => [...prev, { id: nextId(prev), ...input }])
      log('inventario', 'Recurso registrado', input.nombre)
    },
    [log],
  )

  const deleteRecurso = useCallback(
    (id: number) => {
      const item = recursos.find((recurso) => recurso.id === id)
      setRecursos((prev) => prev.filter((recurso) => recurso.id !== id))
      setAsignaciones((prev) => prev.filter((asignacion) => asignacion.recursoId !== id))
      log('inventario', 'Recurso eliminado', item?.nombre ?? `#${id}`)
    },
    [log, recursos],
  )

  const saveTipoRecurso = useCallback(
    (input: TipoRecursoInput, id?: number) => {
      if (id) {
        setTiposRecurso((prev) => prev.map((tipo) => (tipo.id === id ? { ...tipo, ...input } : tipo)))
        log('inventario', 'Tipo de recurso actualizado', input.nombre)
        return
      }
      setTiposRecurso((prev) => [...prev, { id: nextId(prev), ...input }])
      log('inventario', 'Tipo de recurso registrado', input.nombre)
    },
    [log],
  )

  const deleteTipoRecurso = useCallback(
    (id: number) => {
      const enUso = recursos.some((recurso) => recurso.tipoId === id)
      if (enUso) return { ok: false, error: 'No se puede eliminar: hay recursos asociados a este tipo.' }
      const item = tiposRecurso.find((tipo) => tipo.id === id)
      setTiposRecurso((prev) => prev.filter((tipo) => tipo.id !== id))
      log('inventario', 'Tipo de recurso eliminado', item?.nombre ?? `#${id}`)
      return { ok: true }
    },
    [log, recursos, tiposRecurso],
  )

  const addAsignacion = useCallback(
    (input: AsignacionInput) => {
      const recurso = recursos.find((item) => item.id === input.recursoId)
      if (!recurso || recurso.estado !== 'Disponible') {
        return { ok: false, error: 'El recurso ya no está disponible.' }
      }
      setAsignaciones((prev) => [
        ...prev,
        {
          id: nextId(prev),
          recursoId: input.recursoId,
          usuarioId: input.usuarioId,
          fechaAsignacion: '2026-07-10',
          fechaDevolucionEsperada: input.fechaDevolucionEsperada,
          fechaDevolucionReal: null,
          estado: 'Pendiente',
          notas: input.notas,
        },
      ])
      setRecursos((prev) => prev.map((item) => (item.id === input.recursoId ? { ...item, estado: 'Asignado' } : item)))
      log('inventario', 'Recurso asignado', recurso.nombre)
      return { ok: true }
    },
    [log, recursos],
  )

  const devolverAsignacion = useCallback(
    (id: number) => {
      const asignacion = asignaciones.find((item) => item.id === id)
      setAsignaciones((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, estado: 'Devuelto', fechaDevolucionReal: '2026-07-10' }
            : item,
        ),
      )
      if (asignacion) {
        setRecursos((prev) =>
          prev.map((recurso) =>
            recurso.id === asignacion.recursoId ? { ...recurso, estado: 'Disponible' } : recurso,
          ),
        )
        log('inventario', 'Recurso devuelto', `Asignación #${id}`)
      }
    },
    [asignaciones, log],
  )

  const saveTarea = useCallback(
    (input: TareaInput, id?: number) => {
      if (id) {
        setTareas((prev) => prev.map((tarea) => (tarea.id === id ? { ...tarea, ...input } : tarea)))
        log('tarea', 'Tarea actualizada', input.nombre)
        return
      }
      setTareas((prev) => [
        ...prev,
        { id: nextId(prev), creadorId: DEMO_USER.id, estado: 'Pendiente', ...input },
      ])
      log('tarea', 'Tarea registrada', input.nombre)
      notify('tarea', 'Tarea asignada', `Te asignaron: ${input.nombre}.`)
    },
    [log, notify],
  )

  const deleteTarea = useCallback(
    (id: number) => {
      const item = tareas.find((tarea) => tarea.id === id)
      setTareas((prev) => prev.filter((tarea) => tarea.id !== id))
      log('tarea', 'Tarea eliminada', item?.nombre ?? `#${id}`)
    },
    [log, tareas],
  )

  const setTareaEstado = useCallback(
    (id: number, estado: EstadoTarea) => {
      const item = tareas.find((tarea) => tarea.id === id)
      setTareas((prev) => prev.map((tarea) => (tarea.id === id ? { ...tarea, estado } : tarea)))
      if (estado === 'Completada' && item) {
        log('tarea', 'Tarea completada', item.nombre)
        notify('tarea', 'Tarea completada', `Se completó: ${item.nombre}.`)
      }
    },
    [log, notify, tareas],
  )

  const saveGuion = useCallback(
    (input: GuionInput, id?: number) => {
      if (id) {
        setGuiones((prev) =>
          prev.map((guion) =>
            guion.id === id
              ? { ...guion, ...input, modificado: new Date().toISOString() }
              : guion,
          ),
        )
        log('guion', 'Guion actualizado', input.nombre)
        return id
      }
      let newId = 0
      setGuiones((prev) => {
        newId = nextId(prev)
        const base = prev.reduce(
          (max, guion) => Math.max(max, ...guion.elementos.map((elemento) => elemento.id)),
          0,
        )
        return [
          ...prev,
          {
            id: newId,
            ...input,
            estado: 'Borrador',
            modificado: new Date().toISOString(),
            elementos: input.elementos.map((elemento, index) => ({ ...elemento, id: base + index + 1 })),
          },
        ]
      })
      log('guion', 'Guion registrado', input.nombre)
      return newId
    },
    [log],
  )

  const deleteGuion = useCallback(
    (id: number) => {
      const item = guiones.find((guion) => guion.id === id)
      setGuiones((prev) => prev.filter((guion) => guion.id !== id))
      log('guion', 'Guion eliminado', item?.nombre ?? `#${id}`)
    },
    [guiones, log],
  )

  const publicarGuion = useCallback(
    (id: number) => {
      const item = guiones.find((guion) => guion.id === id)
      setGuiones((prev) =>
        prev.map((guion) => (guion.id === id ? { ...guion, estado: 'Publicado' } : guion)),
      )
      log('guion', 'Guion publicado', item?.nombre ?? `#${id}`)
      notify('guion', 'Guion publicado', `${item?.nombre ?? 'El guion'} ya está visible para el equipo.`)
    },
    [guiones, log, notify],
  )

  const replicarGuion = useCallback(
    (id: number, nombre: string, fecha: string) => {
      const original = guiones.find((guion) => guion.id === id)
      let newId = 0
      setGuiones((prev) => {
        newId = nextId(prev)
        const base = prev.reduce(
          (max, guion) => Math.max(max, ...guion.elementos.map((elemento) => elemento.id)),
          0,
        )
        const elementos = (original?.elementos ?? []).map((elemento, index) => ({
          ...elemento,
          id: base + index + 1,
          estado: 'Pendiente' as const,
        }))
        return [
          ...prev,
          {
            id: newId,
            nombre,
            fecha,
            estado: 'Borrador' as const,
            tiempoInning: original?.tiempoInning ?? 120,
            modificado: new Date().toISOString(),
            elementos,
          },
        ]
      })
      log('guion', 'Guion replicado', nombre)
      return newId
    },
    [guiones, log],
  )

  const updateGuionEstado = useCallback(
    (id: number, estado: EstadoGuion) => {
      setGuiones((prev) =>
        prev.map((guion) => {
          if (guion.id === id) return { ...guion, estado }
          if (estado === 'En vivo' && guion.estado === 'En vivo') return { ...guion, estado: 'Publicado' }
          return guion
        }),
      )
    },
    [],
  )

  const saveUsuario = useCallback(
    (input: UsuarioInput, id?: number) => {
      if (id) {
        setUsuarios((prev) =>
          prev.map((usuario) =>
            usuario.id === id
              ? { ...usuario, ...input, iniciales: input.nombre.split(' ').slice(0, 2).map((part) => part.charAt(0)).join('') }
              : usuario,
          ),
        )
        log('sistema', 'Usuario actualizado', input.nombre)
        return
      }
      setUsuarios((prev) => [
        ...prev,
        {
          id: nextId(prev),
          ...input,
          activo: input.activo ?? true,
          ultimoAcceso: new Date().toISOString(),
          iniciales: input.nombre.split(' ').slice(0, 2).map((part) => part.charAt(0)).join(''),
        },
      ])
      log('sistema', 'Usuario registrado', input.nombre)
    },
    [log],
  )

  const deleteUsuario = useCallback(
    (id: number) => {
      const item = usuarios.find((usuario) => usuario.id === id)
      setUsuarios((prev) => prev.filter((usuario) => usuario.id !== id))
      log('sistema', 'Usuario eliminado', item?.nombre ?? `#${id}`)
    },
    [log, usuarios],
  )

  const markRead = useCallback((id: number) => {
    setNotificaciones((prev) => prev.map((item) => (item.id === id ? { ...item, leida: true } : item)))
  }, [])

  const markAllRead = useCallback(() => {
    setNotificaciones((prev) => prev.map((item) => ({ ...item, leida: true })))
  }, [])

  const resetDemo = useCallback(() => {
    setPatrocinadores(PATROCINADORES)
    setContratos(CONTRATOS)
    setPagos(PAGOS)
    setRecursos(RECURSOS)
    setTiposRecurso(TIPOS_RECURSO)
    setAsignaciones(ASIGNACIONES)
    setTareas(TAREAS)
    setGuiones(GUIONES)
    setUsuarios(USUARIOS)
    setNotificaciones(NOTIFICACIONES)
    setActividad(ACTIVIDAD)
  }, [])

  const value = useMemo<DataContextValue>(
    () => ({
      patrocinadores,
      contratos,
      pagos,
      recursos,
      tiposRecurso,
      asignaciones,
      tareas,
      guiones,
      usuarios,
      notificaciones,
      actividad,
      unreadCount: notificaciones.filter((item) => !item.leida).length,
      savePatrocinador,
      deletePatrocinador,
      addPago,
      updatePago,
      deletePago,
      saveRecurso,
      deleteRecurso,
      saveTipoRecurso,
      deleteTipoRecurso,
      addAsignacion,
      devolverAsignacion,
      saveTarea,
      deleteTarea,
      setTareaEstado,
      saveGuion,
      deleteGuion,
      publicarGuion,
      replicarGuion,
      updateGuionEstado,
      saveUsuario,
      deleteUsuario,
      notify,
      markRead,
      markAllRead,
      resetDemo,
    }),
    [
      patrocinadores,
      contratos,
      pagos,
      recursos,
      tiposRecurso,
      asignaciones,
      tareas,
      guiones,
      usuarios,
      notificaciones,
      actividad,
      savePatrocinador,
      deletePatrocinador,
      addPago,
      updatePago,
      deletePago,
      saveRecurso,
      deleteRecurso,
      saveTipoRecurso,
      deleteTipoRecurso,
      addAsignacion,
      devolverAsignacion,
      saveTarea,
      deleteTarea,
      setTareaEstado,
      saveGuion,
      deleteGuion,
      publicarGuion,
      replicarGuion,
      updateGuionEstado,
      saveUsuario,
      deleteUsuario,
      notify,
      markRead,
      markAllRead,
      resetDemo,
    ],
  )

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>
}

export function useData() {
  const context = useContext(DataContext)
  if (!context) throw new Error('useData debe usarse dentro de DataProvider')
  return context
}

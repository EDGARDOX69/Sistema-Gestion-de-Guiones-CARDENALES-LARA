import { ArrowLeftRight, LockKeyhole } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useSession } from '@/hooks/useSession'
import { MODULO_POR_ID } from '@/lib/constants'
import type { ModuleId } from '@/types'
import type { ReactNode } from 'react'

export function ModuleLocked({ module }: { module: ModuleId }) {
  const { selectedModule, clearModule } = useSession()
  const navigate = useNavigate()
  const actual = selectedModule ? MODULO_POR_ID[selectedModule] : null
  const intento = MODULO_POR_ID[module]

  const cambiar = () => {
    clearModule()
    navigate('/modulos')
  }

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-lg items-center justify-center">
      <Card className="w-full p-8 text-center">
        <span className="mx-auto grid size-12 place-items-center rounded-full bg-danger-soft text-danger">
          <LockKeyhole className="size-5" />
        </span>
        <h1 className="mt-4 text-xl font-bold text-ink">Módulo no asignado</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Tu sesión está enfocada en <strong className="text-ink">{actual?.nombre ?? 'un módulo'}</strong>. El
          módulo <strong className="text-ink">{intento.nombre}</strong> no está disponible en esta sesión.
        </p>
        <div className="mt-6 flex flex-col justify-center gap-2 sm:flex-row">
          {actual && (
            <Button onClick={() => navigate(actual.ruta)}>
              Ir a {actual.nombre}
            </Button>
          )}
          <Button variant="secondary" onClick={cambiar} leftIcon={<ArrowLeftRight className="size-4" />}>
            Cambiar módulo
          </Button>
        </div>
      </Card>
    </div>
  )
}

export function ModuleGuard({ module, children }: { module: ModuleId; children: ReactNode }) {
  const { selectedModule } = useSession()
  if (selectedModule !== module) return <ModuleLocked module={module} />
  return <>{children}</>
}

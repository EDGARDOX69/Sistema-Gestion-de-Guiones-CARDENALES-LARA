import { ArrowLeft, Compass } from 'lucide-react'
import { Link } from 'react-router-dom'
import { FieldLines } from '@/components/brand/FieldLines'
import { Logo } from '@/components/brand/Logo'
import { Button } from '@/components/ui/Button'
import { useSession } from '@/hooks/useSession'

export function NotFoundPage() {
  const { user } = useSession()
  const destino = user ? '/app/dashboard' : '/login'

  return (
    <div className="relative flex min-h-dvh flex-col overflow-hidden bg-canvas">
      <FieldLines className="pointer-events-none absolute -right-32 -top-32 size-[520px] text-brand/[0.05]" />
      <header className="relative z-10 p-5 sm:p-8">
        <Logo />
      </header>
      <main className="relative z-10 flex flex-1 items-center justify-center px-4 pb-16">
        <div className="max-w-lg text-center">
          <span className="mx-auto grid size-14 place-items-center rounded-full bg-brand-soft text-brand">
            <Compass className="size-6" />
          </span>
          <p className="display mt-5 text-7xl font-bold leading-none text-ink sm:text-8xl">404</p>
          <h1 className="display mt-3 text-3xl font-semibold text-ink">Esta página no está en el guion.</h1>
          <p className="mt-3 text-sm leading-relaxed text-ink-muted">
            La ruta que buscas no existe o el elemento fue movido. Vuelve al panel para retomar la jornada.
          </p>
          <Button asChild className="mt-6" leftIcon={<ArrowLeft className="size-4" />}>
            <Link to={destino}>{user ? 'Volver al dashboard' : 'Volver al inicio de sesión'}</Link>
          </Button>
        </div>
      </main>
    </div>
  )
}

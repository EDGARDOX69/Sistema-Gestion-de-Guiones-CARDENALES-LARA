import { ArrowLeft, MailCheck } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { AuthShell } from '@/components/layout/AuthShell'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export function RecoverySentPage() {
  const location = useLocation()
  const email = (location.state as { email?: string } | null)?.email

  return (
    <AuthShell
      heroTitle="Recupera el acceso al palco."
      heroDescription="El enlace de recuperación tiene vigencia limitada. Si no llega en unos minutos, revisa el correo no deseado."
    >
      <Card className="p-6 text-center sm:p-8">
        <span className="mx-auto grid size-14 place-items-center rounded-full bg-live-soft text-live">
          <MailCheck className="size-6" />
        </span>
        <p className="eyebrow mt-4">Correo enviado</p>
        <h2 className="display mt-1 text-3xl font-semibold text-ink">Revisa tu bandeja</h2>
        <p className="mt-3 text-sm leading-relaxed text-ink-muted">
          Si <strong className="text-ink">{email ?? 'el correo indicado'}</strong> está registrado, recibirás un
          enlace para restablecer tu contraseña.
        </p>
        <div className="mt-6 space-y-2">
          <Button asChild className="w-full">
            <Link to="/login">Volver al inicio de sesión</Link>
          </Button>
          <Button asChild variant="secondary" className="w-full">
            <Link to="/restablecer">Ver pantalla de restablecimiento</Link>
          </Button>
        </div>
        <Link
          to="/login"
          className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted transition-colors hover:text-ink"
        >
          <ArrowLeft className="size-3.5" />
          Volver
        </Link>
      </Card>
    </AuthShell>
  )
}

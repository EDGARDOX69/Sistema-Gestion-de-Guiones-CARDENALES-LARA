import { CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { AuthShell } from '@/components/layout/AuthShell'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export function ResetSuccessPage() {
  return (
    <AuthShell
      heroTitle="Todo listo para volver."
      heroDescription="Tu contraseña fue actualizada. Ya puedes ingresar con tus nuevas credenciales y retomar la jornada."
    >
      <Card className="p-6 text-center sm:p-8">
        <span className="mx-auto grid size-16 place-items-center rounded-full bg-live-soft text-live">
          <CheckCircle2 className="size-7" />
        </span>
        <p className="eyebrow mt-4">Contraseña actualizada</p>
        <h2 className="display mt-1 text-3xl font-semibold text-ink">Acceso restablecido</h2>
        <p className="mt-3 text-sm leading-relaxed text-ink-muted">
          La nueva contraseña ya está activa. Por seguridad, las sesiones anteriores quedaron cerradas.
        </p>
        <Button asChild className="mt-6 w-full" size="lg">
          <Link to="/login">Iniciar sesión</Link>
        </Button>
      </Card>
    </AuthShell>
  )
}

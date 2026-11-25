import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { AuthShell } from '@/components/layout/AuthShell'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PasswordInput } from '@/components/ui/Input'
import { sleep } from '@/lib/format'
import { resetSchema, type ResetForm } from '@/lib/schemas'

const LEVELS = ['Muy débil', 'Débil', 'Aceptable', 'Fuerte', 'Excelente']
const LEVEL_COLORS = ['bg-danger', 'bg-danger', 'bg-time', 'bg-info', 'bg-live']

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const form = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
    defaultValues: { password: '', confirm: '' },
  })
  const password = form.watch('password')
  const score = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[a-z]/.test(password),
    /[0-9]/.test(password),
  ].filter(Boolean).length

  const onSubmit = async () => {
    await sleep(650)
    toast.success('Contraseña actualizada')
    navigate('/restablecer/completado')
  }

  return (
    <AuthShell
      heroTitle="Define una nueva contraseña."
      heroDescription="Usa una clave distinta a la anterior. El sistema exige mayúscula, minúscula y número para proteger la operación."
    >
      <Card className="p-6 sm:p-8">
        <span className="grid size-11 place-items-center rounded-control bg-brand-soft text-brand">
          <LockKeyhole className="size-5" />
        </span>
        <p className="eyebrow mt-4">Nueva contraseña</p>
        <h2 className="display mt-1 text-3xl font-semibold text-ink">Restablecer acceso</h2>
        <p className="mt-2 text-sm text-ink-muted">Define una contraseña segura para volver al palco.</p>

        <form onSubmit={form.handleSubmit(onSubmit)} className="mt-6 space-y-4" noValidate>
          <PasswordInput
            label="Nueva contraseña"
            autoComplete="new-password"
            placeholder="••••••••"
            error={form.formState.errors.password?.message}
            {...form.register('password')}
          />

          <div>
            <div className="flex gap-1.5">
              {Array.from({ length: 4 }, (_, index) => (
                <span
                  key={index}
                  className={`h-1.5 flex-1 rounded-full ${index < score ? LEVEL_COLORS[score] : 'bg-sunken'}`}
                />
              ))}
            </div>
            <p className="mt-1.5 text-[11px] text-ink-muted">{LEVELS[score]}</p>
          </div>

          <PasswordInput
            label="Confirmar contraseña"
            autoComplete="new-password"
            placeholder="••••••••"
            error={form.formState.errors.confirm?.message}
            {...form.register('confirm')}
          />

          <div className="rounded-control border border-line bg-sunken/45 p-3 text-[11px] text-ink-muted">
            <p className="flex items-center gap-1.5 font-semibold text-ink-soft">
              <ShieldCheck className="size-3.5" /> Mínimo 8 caracteres
            </p>
            <p className="mt-1">Incluye al menos una mayúscula, una minúscula y un número.</p>
          </div>

          <Button
            type="submit"
            size="lg"
            className="w-full"
            loading={form.formState.isSubmitting}
            rightIcon={<ArrowRight className="size-4" />}
          >
            Guardar contraseña
          </Button>
        </form>

        <Link
          to="/login"
          className="mt-5 block text-center text-xs font-semibold text-ink-muted transition-colors hover:text-ink"
        >
          Volver al inicio de sesión
        </Link>
      </Card>
    </AuthShell>
  )
}

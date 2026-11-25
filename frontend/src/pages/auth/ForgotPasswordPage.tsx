import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft, ArrowRight, Mail, MailCheck } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { Captcha } from '@/components/auth/captcha'
import { AuthShell } from '@/components/layout/AuthShell'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { CAPTCHA_ENABLED } from '@/lib/constants'
import { sleep } from '@/lib/format'
import { forgotSchema, type ForgotForm } from '@/lib/schemas'

export function ForgotPasswordPage() {
  const navigate = useNavigate()
  const form = useForm<ForgotForm>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { email: '', captcha: '' },
  })

  const onSubmit = async (values: ForgotForm) => {
    await sleep(650)
    navigate('/recuperar/enviado', { state: { email: values.email } })
  }

  return (
    <AuthShell
      heroTitle="Recupera el acceso al palco."
      heroDescription="Enviaremos un enlace de recuperación al correo asociado a tu cuenta. El resto del equipo sigue trabajando mientras tanto."
    >
      <Card className="p-6 sm:p-8">
        <span className="grid size-11 place-items-center rounded-control bg-brand-soft text-brand">
          <MailCheck className="size-5" />
        </span>
        <p className="eyebrow mt-4">Recuperación de acceso</p>
        <h2 className="display mt-1 text-3xl font-semibold text-ink">¿Olvidaste tu contraseña?</h2>
        <p className="mt-2 text-sm text-ink-muted">
          Escribe el correo de tu cuenta. Si está registrado, recibirás un enlace para restablecerla.
        </p>

        <form onSubmit={form.handleSubmit(onSubmit)} className="mt-6 space-y-4" noValidate>
          <Input
            label="Correo electrónico"
            type="email"
            autoComplete="email"
            placeholder="correo@ejemplo.com"
            icon={Mail}
            error={form.formState.errors.email?.message}
            {...form.register('email')}
          />
          {CAPTCHA_ENABLED && (
            <Captcha
              registro={form.register('captcha')}
              error={form.formState.errors.captcha?.message}
            />
          )}
          <Button
            type="submit"
            size="lg"
            className="w-full"
            loading={form.formState.isSubmitting}
            rightIcon={<ArrowRight className="size-4" />}
          >
            Enviar enlace
          </Button>
        </form>

        <Link
          to="/login"
          className="mt-5 flex items-center justify-center gap-1.5 text-xs font-semibold text-ink-muted transition-colors hover:text-ink"
        >
          <ArrowLeft className="size-3.5" />
          Volver al inicio de sesión
        </Link>
      </Card>
    </AuthShell>
  )
}

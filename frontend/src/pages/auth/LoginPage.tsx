import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, KeyRound, Mail, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { Captcha } from '@/components/auth/captcha'
import { AuthShell } from '@/components/layout/AuthShell'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Checkbox } from '@/components/ui/Checkbox'
import { Input, PasswordInput } from '@/components/ui/Input'
import { useSession } from '@/hooks/useSession'
import { CAPTCHA_ENABLED } from '@/lib/constants'
import { sleep } from '@/lib/format'
import { loginSchema, type LoginForm } from '@/lib/schemas'

export function LoginPage() {
  const navigate = useNavigate()
  const { user, login } = useSession()
  const [remember, setRemember] = useState(true)
  const [captchaCodigo, setCaptchaCodigo] = useState('')

  const form = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '', captcha: '' },
  })

  useEffect(() => {
    if (user) navigate('/modulos', { replace: true })
  }, [user, navigate])

  const onSubmit = async (values: LoginForm) => {
    await sleep(650)
    login(values.email)
    navigate('/modulos')
  }

  const completarDemo = () => {
    form.setValue('email', 'keiver@palco.com')
    form.setValue('password', 'Palco2026')
    if (CAPTCHA_ENABLED) form.setValue('captcha', captchaCodigo)
    form.clearErrors()
  }

  return (
    <AuthShell
      heroTitle="El juego se dirige desde aquí."
      heroDescription="Guión, pautas, tareas y recursos en un solo lugar. El palco de operaciones del estadio, listo para la jornada."
    >
      <Card className="p-6 sm:p-8">
        <div className="flex items-start gap-3">
          <span className="grid size-11 shrink-0 place-items-center rounded-control bg-brand-soft text-brand">
            <ShieldCheck className="size-5" />
          </span>
          <div>
            <p className="eyebrow">Acceso al sistema</p>
            <h2 className="display mt-1 text-3xl font-semibold text-ink">Iniciar sesión</h2>
            <p className="mt-1 text-sm text-ink-muted">Ingresa tus credenciales para entrar al palco.</p>
          </div>
        </div>

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
          <PasswordInput
            label="Contraseña"
            autoComplete="current-password"
            placeholder="••••••••"
            error={form.formState.errors.password?.message}
            {...form.register('password')}
          />

          {CAPTCHA_ENABLED && (
            <Captcha
              registro={form.register('captcha')}
              error={form.formState.errors.captcha?.message}
              onCodeChange={setCaptchaCodigo}
            />
          )}

          <div className="flex items-center justify-between gap-3">
            <Checkbox
              checked={remember}
              onCheckedChange={setRemember}
              label="Recordarme"
            />
            <Link
              to="/recuperar"
              className="text-xs font-semibold text-brand transition-colors hover:text-brand-strong"
            >
              Olvidé mi contraseña
            </Link>
          </div>

          <Button
            type="submit"
            size="lg"
            className="w-full"
            loading={form.formState.isSubmitting}
            rightIcon={<ArrowRight className="size-4" />}
          >
            Entrar al palco
          </Button>
        </form>

        <Button type="button" variant="ghost" className="mt-2 w-full" onClick={completarDemo} leftIcon={<KeyRound className="size-4" />}>
          Completar acceso de prueba
        </Button>

        <p className="mt-5 text-center text-[11px] leading-relaxed text-ink-faint">
          Demo visual: usa cualquier correo válido y una clave de 8 caracteres.
        </p>
      </Card>
    </AuthShell>
  )
}

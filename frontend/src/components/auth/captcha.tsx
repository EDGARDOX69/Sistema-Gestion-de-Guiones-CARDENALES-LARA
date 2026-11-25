import { RefreshCw, ShieldQuestion } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { UseFormRegisterReturn } from 'react-hook-form'
import { Input } from '@/components/ui/Input'
import { CAPTCHA_LENGTH } from '@/lib/constants'
import { generarCaptcha } from '@/lib/format'

interface CaptchaProps {
  registro: UseFormRegisterReturn
  error?: string
  onCodeChange?: (code: string) => void
}

export function Captcha({ registro, error, onCodeChange }: CaptchaProps) {
  const [code, setCode] = useState(generarCaptcha)

  useEffect(() => {
    onCodeChange?.(code)
  }, [code, onCodeChange])

  const refrescar = () => {
    setCode(generarCaptcha())
  }

  return (
    <div className="space-y-2">
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <p className="mb-1.5 flex items-center gap-1.5 text-sm font-semibold text-ink-soft">
            <ShieldQuestion className="size-4 text-brand" /> Verificación
          </p>
          <div className="flex gap-1.5 rounded-control border border-line-strong bg-sunken/45 p-2">
            {code.split('').map((caracter, indice) => (
              <span
                key={indice}
                className="captcha-tile grid size-9 flex-1 place-items-center rounded-md bg-surface font-mono text-lg font-bold text-ink shadow-sm"
              >
                {caracter}
              </span>
            ))}
          </div>
        </div>
        <button
          type="button"
          onClick={refrescar}
          aria-label="Generar otro código"
          title="Generar otro código"
          className="captcha-refresh grid size-10 shrink-0 place-items-center rounded-control border border-line-strong bg-sunken/45 text-ink-muted transition-colors hover:border-brand/50 hover:text-brand"
        >
          <RefreshCw className="size-4" />
        </button>
      </div>
      <Input
        {...registro}
        label="Escribe el código"
        placeholder={`${CAPTCHA_LENGTH} caracteres`}
        autoComplete="off"
        error={error}
      />
    </div>
  )
}

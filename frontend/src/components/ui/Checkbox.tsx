import * as CheckboxPrimitive from '@radix-ui/react-checkbox'
import { Check } from 'lucide-react'
import { useId } from 'react'
import { cn } from '@/lib/cn'

interface CheckboxProps {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  label?: string
  description?: string
  disabled?: boolean
  id?: string
  className?: string
}

export function Checkbox({
  checked,
  onCheckedChange,
  label,
  description,
  disabled,
  id,
  className,
}: CheckboxProps) {
  const generatedId = useId()
  const checkboxId = id ?? generatedId

  return (
    <div className={cn('flex items-start gap-2.5', className)}>
      <CheckboxPrimitive.Root
        id={checkboxId}
        checked={checked}
        onCheckedChange={(value) => onCheckedChange(value === true)}
        disabled={disabled}
        className="mt-0.5 grid size-4.5 shrink-0 place-items-center rounded-[5px] border border-line-strong bg-surface transition-colors data-[state=checked]:border-brand data-[state=checked]:bg-brand data-[state=checked]:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        <CheckboxPrimitive.Indicator>
          <Check className="size-3" strokeWidth={3} />
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      {(label || description) && (
        <div className="min-w-0">
          {label && (
            <label htmlFor={checkboxId} className="cursor-pointer text-sm font-medium text-ink-soft">
              {label}
            </label>
          )}
          {description && <p className="text-xs text-ink-muted">{description}</p>}
        </div>
      )}
    </div>
  )
}

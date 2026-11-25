import * as SelectPrimitive from '@radix-ui/react-select'
import { Check, ChevronDown, CircleAlert } from 'lucide-react'
import { useId } from 'react'
import { cn } from '@/lib/cn'

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  options: SelectOption[]
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  id?: string
  className?: string
}

export function Select({
  value,
  onValueChange,
  options,
  placeholder = 'Seleccione...',
  label,
  error,
  disabled,
  id,
  className,
}: SelectProps) {
  const generatedId = useId()
  const selectId = id ?? generatedId

  return (
    <div className={cn('w-full', className)}>
      {label && (
        <label htmlFor={selectId} className="mb-1.5 block text-sm font-semibold text-ink-soft">
          {label}
        </label>
      )}
      <SelectPrimitive.Root value={value || undefined} onValueChange={onValueChange} disabled={disabled}>
        <SelectPrimitive.Trigger
          id={selectId}
          aria-label={label}
          aria-invalid={Boolean(error)}
          className={cn(
            'flex h-11 w-full items-center justify-between gap-2 rounded-control border border-line-strong bg-sunken/45 px-3.5 text-left text-sm text-ink transition-[border-color,box-shadow,background-color] duration-150 focus:border-brand/60 focus:bg-surface focus:outline-none focus:ring-2 focus:ring-brand/15 data-[placeholder]:text-ink-faint disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-danger/50 focus:border-danger focus:ring-danger/15',
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon asChild>
            <ChevronDown className="size-4 text-ink-muted" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            position="popper"
            sideOffset={6}
            className="z-[70] max-h-72 min-w-[var(--radix-select-trigger-width)] overflow-hidden rounded-control border border-line bg-raised text-ink shadow-pop"
          >
            <SelectPrimitive.Viewport className="p-1">
              {options.map((option) => (
                <SelectPrimitive.Item
                  key={option.value}
                  value={option.value}
                  className="relative flex cursor-pointer select-none items-center rounded-md py-2 pl-8 pr-3 text-sm outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[highlighted]:bg-brand-soft data-[highlighted]:text-brand"
                >
                  <span className="absolute left-2.5 flex size-4 items-center justify-center">
                    <SelectPrimitive.ItemIndicator>
                      <Check className="size-3.5" />
                    </SelectPrimitive.ItemIndicator>
                  </span>
                  <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
                </SelectPrimitive.Item>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>
      {error && (
        <p className="mt-1.5 flex items-center gap-1.5 text-xs font-medium text-danger">
          <CircleAlert className="size-3.5" />
          {error}
        </p>
      )}
    </div>
  )
}

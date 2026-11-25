import { Slot } from '@radix-ui/react-slot'
import { Loader2 } from 'lucide-react'
import { Children, cloneElement, isValidElement, type ButtonHTMLAttributes, type ReactElement, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

type Variant = 'primary' | 'secondary' | 'ghost' | 'subtle' | 'danger' | 'live'
type Size = 'sm' | 'md' | 'lg' | 'icon'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  asChild?: boolean
  loading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

const variants: Record<Variant, string> = {
  primary:
    'bg-brand text-white shadow-[0_8px_24px_-12px_color-mix(in_oklab,var(--brand)_70%,transparent)] hover:bg-brand-strong active:scale-[0.98]',
  secondary:
    'border border-line-strong bg-surface text-ink hover:border-brand/40 hover:bg-brand-soft/40 active:scale-[0.98]',
  ghost: 'text-ink-soft hover:bg-sunken hover:text-ink active:scale-[0.98]',
  subtle: 'bg-sunken text-ink-soft hover:bg-line hover:text-ink active:scale-[0.98]',
  danger: 'bg-danger text-white hover:brightness-110 active:scale-[0.98]',
  live: 'bg-live text-night-950 hover:brightness-110 active:scale-[0.98]',
}

const sizes: Record<Size, string> = {
  sm: 'h-9 gap-2 rounded-control px-3 text-xs font-semibold',
  md: 'h-11 gap-2 rounded-control px-4 text-sm font-semibold',
  lg: 'h-12 gap-2.5 rounded-control px-6 text-sm font-bold',
  icon: 'size-10 rounded-control',
}

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  asChild,
  loading,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  if (asChild) {
    const child = Children.only(children)
    if (isValidElement(child)) {
      const element = child as ReactElement<{ children?: ReactNode }>
      return (
        <Slot
          className={cn(
            'inline-flex shrink-0 items-center justify-center whitespace-nowrap transition-[background-color,border-color,color,transform,box-shadow] duration-150',
            variants[variant],
            sizes[size],
            className,
          )}
          {...props}
        >
          {cloneElement(
            element,
            undefined,
            <>
              {leftIcon}
              {element.props.children}
              {rightIcon}
            </>,
          )}
        </Slot>
      )
    }
  }

  return (
    <button
      className={cn(
        'inline-flex shrink-0 items-center justify-center whitespace-nowrap transition-[background-color,border-color,color,transform,box-shadow] duration-150 disabled:pointer-events-none disabled:opacity-50',
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="size-4 animate-spin" />
          {children}
        </>
      ) : (
        <>
          {leftIcon}
          {children}
          {rightIcon}
        </>
      )}
    </button>
  )
}

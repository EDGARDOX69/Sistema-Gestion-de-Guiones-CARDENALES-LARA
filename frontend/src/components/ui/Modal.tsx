import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  icon?: LucideIcon
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizes = {
  sm: 'sm:max-w-md',
  md: 'sm:max-w-lg',
  lg: 'sm:max-w-2xl',
  xl: 'sm:max-w-4xl',
}

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  icon: Icon,
  children,
  footer,
  size = 'md',
  className,
}: ModalProps) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="dialog-overlay fixed inset-0 z-50 bg-night-950/60 backdrop-blur-[2px]" />
        <div className="pointer-events-none fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-6">
          <DialogPrimitive.Content
            aria-describedby={description ? undefined : undefined}
            className={cn(
              'dialog-content pointer-events-auto relative flex max-h-[92dvh] w-full flex-col overflow-hidden rounded-t-sheet border border-line bg-surface text-ink shadow-pop sm:rounded-card',
              sizes[size],
              className,
            )}
          >
            <div className="flex items-start gap-3 border-b border-line p-5">
              {Icon && (
                <span className="grid size-10 shrink-0 place-items-center rounded-control bg-brand-soft text-brand">
                  <Icon className="size-5" />
                </span>
              )}
              <div className="min-w-0 flex-1">
                <DialogPrimitive.Title className="text-base font-bold text-ink">
                  {title}
                </DialogPrimitive.Title>
                {description && (
                  <DialogPrimitive.Description className="mt-1 text-sm text-ink-muted">
                    {description}
                  </DialogPrimitive.Description>
                )}
              </div>
              <DialogPrimitive.Close asChild>
                <button
                  type="button"
                  aria-label="Cerrar"
                  className="grid size-8 shrink-0 place-items-center rounded-md text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
                >
                  <X className="size-4" />
                </button>
              </DialogPrimitive.Close>
            </div>
            <div className="scroll-area min-h-0 flex-1 overflow-y-auto p-5">{children}</div>
            {footer && (
              <div className="flex items-center justify-end gap-2 border-t border-line bg-sunken/35 px-5 py-4">
                {footer}
              </div>
            )}
          </DialogPrimitive.Content>
        </div>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}

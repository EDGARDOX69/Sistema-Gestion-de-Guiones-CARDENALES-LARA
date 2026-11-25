import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { useLockBodyScroll } from '@/hooks/useLockBodyScroll'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface DrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  width?: 'md' | 'lg'
}

export function Drawer({ open, onOpenChange, title, description, children, footer, width = 'md' }: DrawerProps) {
  useLockBodyScroll(open)

  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="dialog-overlay fixed inset-0 z-50 bg-night-950/55 backdrop-blur-[2px]" />
        <div className="fixed inset-0 z-50 flex justify-end">
          <DialogPrimitive.Content
            className={cn(
              'drawer-content flex h-full w-full flex-col overflow-hidden border-l border-line bg-surface text-ink shadow-pop',
              width === 'lg' ? 'sm:max-w-2xl' : 'sm:max-w-md',
            )}
          >
            <div className="flex items-start justify-between gap-4 border-b border-line p-5">
              <div className="min-w-0">
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

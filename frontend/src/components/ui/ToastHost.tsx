import { Toaster } from 'sonner'
import { useTheme } from '@/hooks/useTheme'

export function ToastHost() {
  const { resolvedTheme } = useTheme()
  return (
    <Toaster
      theme={resolvedTheme}
      position="bottom-right"
      closeButton
      toastOptions={{
        classNames: {
          toast: '!rounded-control !border !border-line !bg-raised !text-ink !shadow-pop',
          title: '!text-sm !font-semibold !text-ink',
          description: '!text-xs !text-ink-muted',
          actionButton: '!bg-brand !text-white',
          cancelButton: '!bg-sunken !text-ink-soft',
          closeButton: '!border-line !bg-surface !text-ink-muted',
        },
      }}
    />
  )
}

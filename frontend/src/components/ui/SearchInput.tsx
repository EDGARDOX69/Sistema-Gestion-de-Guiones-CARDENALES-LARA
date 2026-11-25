import { Search, X } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/cn'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  ariaLabel?: string
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Buscar...',
  className,
  ariaLabel = 'Buscar',
}: SearchInputProps) {
  return (
    <Input
      type="search"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      placeholder={placeholder}
      aria-label={ariaLabel}
      icon={Search}
      className={cn('[&::-webkit-search-cancel-button]:hidden', className)}
      rightSlot={
        value ? (
          <button
            type="button"
            onClick={() => onChange('')}
            aria-label="Limpiar búsqueda"
            className="grid size-8 place-items-center rounded-md text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
          >
            <X className="size-4" />
          </button>
        ) : null
      }
    />
  )
}

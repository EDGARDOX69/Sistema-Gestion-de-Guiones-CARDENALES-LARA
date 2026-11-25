import { cn } from '@/lib/cn'

export function FieldLines({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 400"
      fill="none"
      aria-hidden="true"
      className={cn('pointer-events-none select-none', className)}
    >
      <path d="M200 366 L52 218" stroke="currentColor" strokeWidth="1.2" />
      <path d="M200 366 L348 218" stroke="currentColor" strokeWidth="1.2" />
      <path d="M52 218 A200 200 0 0 1 348 218" stroke="currentColor" strokeWidth="1.2" />
      <path d="M200 296 L262 234 L200 172 L138 234 Z" stroke="currentColor" strokeWidth="1.2" />
      <path d="M200 296 L200 366" stroke="currentColor" strokeWidth="0.8" strokeDasharray="3 7" />
      <circle cx="200" cy="366" r="2.2" fill="currentColor" />
      <circle cx="262" cy="234" r="2.2" fill="currentColor" />
      <circle cx="200" cy="172" r="2.2" fill="currentColor" />
      <circle cx="138" cy="234" r="2.2" fill="currentColor" />
      <circle cx="200" cy="234" r="2.2" fill="currentColor" />
    </svg>
  )
}

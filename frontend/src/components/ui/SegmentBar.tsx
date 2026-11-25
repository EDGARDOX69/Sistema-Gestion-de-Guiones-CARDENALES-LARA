import { cn } from '@/lib/cn'

export function SegmentBar({
  segments,
  className,
}: {
  segments: { value: number; className: string }[]
  className?: string
}) {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0)
  return (
    <div className={cn('flex h-2 w-full overflow-hidden rounded-full bg-sunken', className)}>
      {segments.map((segment, index) => (
        <div
          key={index}
          className={segment.className}
          style={{ width: `${total > 0 ? (segment.value / total) * 100 : 0}%` }}
        />
      ))}
    </div>
  )
}

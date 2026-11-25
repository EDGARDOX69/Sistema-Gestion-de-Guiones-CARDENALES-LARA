import { Boxes, ClipboardCheck, Handshake, ScrollText, Wallet } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { ModuleId } from '@/types'

const ICONS: Record<ModuleId, LucideIcon> = {
  patrocinantes: Handshake,
  balance: Wallet,
  inventario: Boxes,
  tareas: ClipboardCheck,
  guion: ScrollText,
}

export function ModuleIcon({ id, className }: { id: ModuleId; className?: string }) {
  const Icon = ICONS[id]
  return <Icon className={className} />
}

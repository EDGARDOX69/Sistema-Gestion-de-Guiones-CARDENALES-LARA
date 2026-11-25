import { useSession } from '@/hooks/useSession'
import { MODULO_POR_ID } from '@/lib/constants'

export function useModule() {
  const { selectedModule, setModule, clearModule } = useSession()
  return {
    selectedModule,
    info: selectedModule ? MODULO_POR_ID[selectedModule] : null,
    setModule,
    clearModule,
  }
}

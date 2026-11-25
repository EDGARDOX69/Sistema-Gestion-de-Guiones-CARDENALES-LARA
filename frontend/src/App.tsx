import { TooltipProvider } from '@radix-ui/react-tooltip'
import { MotionConfig } from 'motion/react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { ModuleGuard } from '@/components/layout/ModuleGuard'
import { RequireModule, RequireSession } from '@/components/layout/RouteGuards'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RecoverySentPage } from '@/pages/auth/RecoverySentPage'
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage'
import { ResetSuccessPage } from '@/pages/auth/ResetSuccessPage'
import { BalancePage } from '@/pages/balance/BalancePage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { EnVivoPage } from '@/pages/guion/EnVivoPage'
import { GuionBuilderPage } from '@/pages/guion/GuionBuilderPage'
import { GuionPage } from '@/pages/guion/GuionPage'
import { InventarioPage } from '@/pages/inventario/InventarioPage'
import { ModuleSelectPage } from '@/pages/modules/ModuleSelectPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { PatrocinadoresPage } from '@/pages/patrocinadores/PatrocinadoresPage'
import { PerfilPage } from '@/pages/perfil/PerfilPage'
import { TareasPage } from '@/pages/tareas/TareasPage'
import { UsuariosPage } from '@/pages/usuarios/UsuariosPage'

export function App() {
  return (
    <TooltipProvider delayDuration={200}>
      <MotionConfig reducedMotion="user">
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/recuperar" element={<ForgotPasswordPage />} />
        <Route path="/recuperar/enviado" element={<RecoverySentPage />} />
        <Route path="/restablecer" element={<ResetPasswordPage />} />
        <Route path="/restablecer/completado" element={<ResetSuccessPage />} />

        <Route element={<RequireSession />}>
          <Route path="/modulos" element={<ModuleSelectPage />} />
          <Route element={<RequireModule />}>
            <Route
              path="/app/guion/:id/en-vivo"
              element={
                <ModuleGuard module="guion">
                  <EnVivoPage />
                </ModuleGuard>
              }
            />
            <Route element={<AppShell />}>
              <Route path="/app/dashboard" element={<DashboardPage />} />
              <Route
                path="/app/patrocinantes"
                element={
                  <ModuleGuard module="patrocinantes">
                    <PatrocinadoresPage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/balance"
                element={
                  <ModuleGuard module="balance">
                    <BalancePage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/inventario"
                element={
                  <ModuleGuard module="inventario">
                    <InventarioPage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/tareas"
                element={
                  <ModuleGuard module="tareas">
                    <TareasPage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/guion"
                element={
                  <ModuleGuard module="guion">
                    <GuionPage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/guion/nuevo"
                element={
                  <ModuleGuard module="guion">
                    <GuionBuilderPage />
                  </ModuleGuard>
                }
              />
              <Route
                path="/app/guion/:id/editar"
                element={
                  <ModuleGuard module="guion">
                    <GuionBuilderPage />
                  </ModuleGuard>
                }
              />
              <Route path="/app/perfil" element={<PerfilPage />} />
              <Route path="/app/usuarios" element={<UsuariosPage />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      </MotionConfig>
    </TooltipProvider>
  )
}

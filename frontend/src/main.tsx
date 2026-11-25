import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import '@fontsource/barlow-condensed/500.css'
import '@fontsource/barlow-condensed/600.css'
import '@fontsource/barlow-condensed/700.css'
import '@fontsource/manrope/400.css'
import '@fontsource/manrope/500.css'
import '@fontsource/manrope/600.css'
import '@fontsource/manrope/700.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
import '@fontsource/jetbrains-mono/600.css'
import './styles/globals.css'
import { App } from '@/App'
import { DataProvider } from '@/context/DataProvider'
import { LiveProvider } from '@/context/LiveProvider'
import { SessionProvider } from '@/context/SessionProvider'
import { ThemeProvider } from '@/context/ThemeProvider'
import { ToastHost } from '@/components/ui/ToastHost'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <SessionProvider>
        <DataProvider>
          <LiveProvider>
            <BrowserRouter>
              <App />
              <ToastHost />
            </BrowserRouter>
          </LiveProvider>
        </DataProvider>
      </SessionProvider>
    </ThemeProvider>
  </StrictMode>,
)

'use client'

import { ReactNode } from 'react'
import { GameStateProvider } from '../lib/store/gameStore'
import { AuthProvider } from '../lib/store/authStore'

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      <GameStateProvider>
        {children}
      </GameStateProvider>
    </AuthProvider>
  )
}
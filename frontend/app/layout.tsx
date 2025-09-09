import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Echopolis - 回声都市',
  description: 'AI驱动的社会金融模拟器',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className="dark">
      <body className={`${inter.className} bg-neutral-900 text-neutral-100`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#262626',
                color: '#f5f5f5',
                border: '1px solid #404040',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
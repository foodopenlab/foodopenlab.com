import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { RootNavigationGate } from '@/components/admin/root-navigation-gate'
import { ThemeProvider } from '@/components/theme/theme-provider'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'HACCP Monitor AI | 위해식품 실시간 모니터링',
  description: '식품안전나라 공공 API와 연동하여 위해식품 회수 정보를 AI가 실시간으로 모니터링합니다. HACCP 담당자를 위한 스마트 모니터링 솔루션.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="flex min-h-screen flex-col overflow-x-clip font-sans antialiased">
        <ThemeProvider>
          <RootNavigationGate />
          <div className="flex min-h-0 flex-1 flex-col">{children}</div>
          {process.env.NODE_ENV === 'production' && <Analytics />}
        </ThemeProvider>
      </body>
    </html>
  )
}

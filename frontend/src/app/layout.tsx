import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Nav from '@/components/Nav'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'RunCast Intelligence — Search Running Podcasts',
  description: 'Ask anything about running. Get answers from thousands of podcast episodes with timestamps and sources.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  )
}

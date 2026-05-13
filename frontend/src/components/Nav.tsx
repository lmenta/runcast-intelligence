'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Mic } from 'lucide-react'

const links = [
  { href: '/', label: 'Search' },
  { href: '/podcasts', label: 'Podcasts' },
  { href: '/episodes', label: 'Episodes' },
]

export default function Nav() {
  const path = usePathname()
  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2 font-bold text-gray-900">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-500 text-white">
            <Mic size={14} />
          </span>
          <span>RunCast</span>
          <span className="text-xs font-normal text-gray-400">Intelligence</span>
        </Link>
        <div className="flex items-center gap-1">
          {links.map(l => (
            <Link
              key={l.href}
              href={l.href}
              className={`rounded-lg px-3 py-1.5 text-sm transition-colors ${
                path === l.href
                  ? 'bg-orange-50 font-medium text-orange-600'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  )
}

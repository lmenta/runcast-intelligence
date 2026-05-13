'use client'
import { Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

interface Props {
  defaultValue?: string
  autoFocus?: boolean
  size?: 'lg' | 'md'
}

export default function SearchBar({ defaultValue = '', autoFocus, size = 'lg' }: Props) {
  const [query, setQuery] = useState(defaultValue)
  const router = useRouter()

  const submit = (q: string) => {
    const trimmed = q.trim()
    if (!trimmed) return
    router.push(`/search?q=${encodeURIComponent(trimmed)}`)
  }

  const isLg = size === 'lg'

  return (
    <form
      onSubmit={e => { e.preventDefault(); submit(query) }}
      className={`flex w-full items-center gap-3 rounded-2xl border-2 border-gray-200 bg-white shadow-sm transition-all focus-within:border-orange-400 focus-within:shadow-md ${isLg ? 'px-5 py-4' : 'px-4 py-3'}`}
    >
      <Search size={isLg ? 20 : 16} className="shrink-0 text-gray-400" />
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Ask anything about running…"
        autoFocus={autoFocus}
        className={`flex-1 bg-transparent outline-none placeholder:text-gray-400 ${isLg ? 'text-lg' : 'text-base'} text-gray-900`}
      />
      <button
        type="submit"
        className="shrink-0 rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-orange-600 disabled:opacity-40"
        disabled={!query.trim()}
      >
        Search
      </button>
    </form>
  )
}

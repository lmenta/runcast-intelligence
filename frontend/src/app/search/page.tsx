import { Suspense } from 'react'
import SearchBar from '@/components/SearchBar'
import AnswerCard from '@/components/AnswerCard'
import SourceCard from '@/components/SourceCard'
import { mockSearchResponse } from '@/lib/mock'
import { SearchResponse } from '@/lib/types'
import { Loader2 } from 'lucide-react'

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

async function fetchSearch(query: string): Promise<SearchResponse | null> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 400)) // simulate latency
    return { ...mockSearchResponse, query }
  }
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/search`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 8 }),
        cache: 'no-store',
      }
    )
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

async function Results({ query }: { query: string }) {
  const data = await fetchSearch(query)

  if (!data) {
    return (
      <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-600">
        Could not reach the search API. Make sure the backend is running on port 8000.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <AnswerCard answer={data.answer} query={query} />
      {data.sources.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
            Sources ({data.sources.length})
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {data.sources.map((s, i) => (
              <SourceCard key={s.chunk_id} source={s} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <Suspense>
        <SearchPageInner searchParams={searchParams} />
      </Suspense>
    </div>
  )
}

async function SearchPageInner({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams
  const query = q?.trim() || ''

  return (
    <div className="space-y-6">
      <SearchBar defaultValue={query} size="md" />

      {!query ? (
        <p className="text-center text-gray-400">Enter a question above to search.</p>
      ) : (
        <Suspense
          fallback={
            <div className="flex items-center justify-center gap-2 py-16 text-gray-400">
              <Loader2 size={18} className="animate-spin" />
              Searching podcast transcripts…
            </div>
          }
        >
          <Results query={query} />
        </Suspense>
      )}
    </div>
  )
}

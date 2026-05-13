import SearchBar from '@/components/SearchBar'
import { mockStats } from '@/lib/mock'

const EXAMPLE_QUERIES = [
  'How do elites taper for a marathon?',
  'Best nutrition strategy for ultramarathons',
  'What causes IT band syndrome?',
  'How to run your first sub-3 hour marathon',
  'Trail running vs road running training differences',
  'How much sleep do elite runners get?',
]

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

async function getStats() {
  if (USE_MOCK) return mockStats
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/stats`,
      { next: { revalidate: 300 } }
    )
    if (!res.ok) return mockStats
    return res.json()
  } catch {
    return mockStats
  }
}

export default async function HomePage() {
  const stats = await getStats()

  return (
    <div className="mx-auto max-w-3xl px-6 py-20">
      {/* Hero */}
      <div className="mb-12 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-medium text-orange-600">
          🎙 {stats.episodes_indexed.toLocaleString()} episodes indexed across {stats.podcasts} podcasts
        </div>
        <h1 className="mb-4 text-4xl font-bold leading-tight tracking-tight text-gray-900 sm:text-5xl">
          Ask anything about<br />
          <span className="text-orange-500">running</span>
        </h1>
        <p className="mx-auto max-w-md text-lg text-gray-500">
          Semantic search across thousands of hours of running podcast transcripts.
          Get answers with sources and timestamps.
        </p>
      </div>

      {/* Search bar */}
      <div className="mb-8">
        <SearchBar autoFocus size="lg" />
      </div>

      {/* Example queries */}
      <div className="mb-16">
        <p className="mb-3 text-center text-xs font-medium uppercase tracking-wide text-gray-400">
          Try asking
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {EXAMPLE_QUERIES.map(q => (
            <a
              key={q}
              href={`/search?q=${encodeURIComponent(q)}`}
              className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 transition-colors hover:border-orange-300 hover:text-orange-600"
            >
              {q}
            </a>
          ))}
        </div>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-2 gap-4 rounded-2xl border border-gray-200 bg-white p-6">
        {[
          { value: stats.podcasts, label: 'Podcasts' },
          { value: stats.episodes_indexed.toLocaleString(), label: 'Episodes indexed' },
        ].map(s => (
          <div key={s.label} className="text-center">
            <div className="text-2xl font-bold text-gray-900">{s.value}</div>
            <div className="text-xs text-gray-500 mt-0.5">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

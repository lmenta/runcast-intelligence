import { Suspense } from 'react'
import EpisodeCard from '@/components/EpisodeCard'
import { mockEpisodes } from '@/lib/mock'
import { Episode } from '@/lib/types'

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

async function getEpisodes(params: { podcast_id?: string; status?: string }): Promise<Episode[]> {
  if (USE_MOCK) return mockEpisodes
  try {
    const qs = new URLSearchParams({ limit: '40', ...params })
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/episodes?${qs}`,
      { next: { revalidate: 60 } }
    )
    if (!res.ok) return mockEpisodes
    return res.json()
  } catch {
    return mockEpisodes
  }
}

const STATUS_TABS = ['all', 'ready', 'pending', 'failed']

export default function EpisodesPage({
  searchParams,
}: {
  searchParams: Promise<{ podcast_id?: string; status?: string }>
}) {
  return (
    <Suspense>
      <EpisodesPageInner searchParams={searchParams} />
    </Suspense>
  )
}

async function EpisodesPageInner({
  searchParams,
}: {
  searchParams: Promise<{ podcast_id?: string; status?: string }>
}) {
  const { podcast_id, status } = await searchParams
  const episodes = await getEpisodes({ podcast_id, status })
  const activeStatus = status || 'all'

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Episodes</h1>
        <p className="mt-1 text-gray-500">{episodes.length} episodes</p>
      </div>

      {/* Status filter tabs */}
      <div className="mb-6 flex gap-2 border-b border-gray-200">
        {STATUS_TABS.map(s => (
          <a
            key={s}
            href={`/episodes${s !== 'all' ? `?status=${s}` : ''}`}
            className={`px-3 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              activeStatus === s
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            {s}
          </a>
        ))}
      </div>

      <div className="space-y-3">
        {episodes.length === 0 ? (
          <p className="py-10 text-center text-gray-400">No episodes found.</p>
        ) : (
          episodes.map(ep => <EpisodeCard key={ep.id} episode={ep} />)
        )}
      </div>
    </div>
  )
}

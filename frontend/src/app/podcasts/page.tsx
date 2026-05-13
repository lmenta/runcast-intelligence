import PodcastCard from '@/components/PodcastCard'
import { mockPodcasts } from '@/lib/mock'
import { Podcast } from '@/lib/types'

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

async function getPodcasts(): Promise<Podcast[]> {
  if (USE_MOCK) return mockPodcasts
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/podcasts`,
      { next: { revalidate: 600 } }
    )
    if (!res.ok) return mockPodcasts
    return res.json()
  } catch {
    return mockPodcasts
  }
}

export default async function PodcastsPage() {
  const podcasts = await getPodcasts()

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Podcasts</h1>
        <p className="mt-1 text-gray-500">
          {podcasts.length} shows indexed — all episodes are searchable.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {podcasts.map(p => (
          <PodcastCard key={p.id} podcast={p} />
        ))}
      </div>
    </div>
  )
}

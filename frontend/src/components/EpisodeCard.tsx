import { Clock, Radio } from 'lucide-react'
import { Episode } from '@/lib/types'
import Link from 'next/link'

function formatDuration(secs: number | null) {
  if (!secs) return null
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

function formatDate(iso: string | null) {
  if (!iso) return null
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

const statusColors: Record<string, string> = {
  ready: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  transcribing: 'bg-blue-100 text-blue-700',
  transcribed: 'bg-purple-100 text-purple-700',
  embedding: 'bg-indigo-100 text-indigo-700',
  failed: 'bg-red-100 text-red-700',
}

export default function EpisodeCard({ episode }: { episode: Episode }) {
  const duration = formatDuration(episode.duration_secs)
  const date = formatDate(episode.published_at)

  return (
    <div className="flex items-start gap-4 rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-orange-100 text-orange-500">
        <Radio size={18} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-gray-900 leading-snug line-clamp-2">{episode.title}</p>
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
          {episode.podcast_name && (
            <span className="text-xs font-medium text-orange-600">{episode.podcast_name}</span>
          )}
          {date && <span className="text-xs text-gray-400">{date}</span>}
          {duration && (
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <Clock size={10} />
              {duration}
            </span>
          )}
        </div>
      </div>
      <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[episode.status] || 'bg-gray-100 text-gray-600'}`}>
        {episode.status}
      </span>
    </div>
  )
}

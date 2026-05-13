import { Clock, Podcast } from 'lucide-react'
import { SourceChunk } from '@/lib/types'

function formatTimestamp(secs: number | null) {
  if (secs === null) return null
  const m = Math.floor(secs / 60)
  const s = Math.floor(secs % 60)
  const h = Math.floor(m / 60)
  if (h > 0) return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

function formatDate(iso: string | null) {
  if (!iso) return null
  return new Date(iso).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' })
}

export default function SourceCard({ source, index }: { source: SourceChunk; index: number }) {
  const ts = formatTimestamp(source.start_secs)
  const date = formatDate(source.published_at)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm">
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-500">
            {index}
          </span>
          <div className="min-w-0">
            <p className="truncate font-medium text-gray-900 text-sm">{source.episode_title}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="flex items-center gap-1 text-xs text-orange-600">
                <Podcast size={10} />
                {source.podcast_name}
              </span>
              {date && <span className="text-xs text-gray-400">{date}</span>}
            </div>
          </div>
        </div>
        {ts && (
          <span className="flex shrink-0 items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
            <Clock size={10} />
            {ts}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
        "{source.excerpt}"
      </p>
    </div>
  )
}

import { ExternalLink, Mic } from 'lucide-react'
import { Podcast } from '@/lib/types'
import Link from 'next/link'

export default function PodcastCard({ podcast }: { podcast: Podcast }) {
  return (
    <div className="group flex flex-col rounded-2xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-100 text-orange-500">
        <Mic size={22} />
      </div>
      <h3 className="mb-1 font-semibold text-gray-900 leading-snug">{podcast.name}</h3>
      {podcast.description && (
        <p className="mb-3 flex-1 text-sm text-gray-500 leading-relaxed line-clamp-3">
          {podcast.description}
        </p>
      )}
      <div className="flex items-center gap-3 mt-auto">
        <Link
          href={`/episodes?podcast_id=${podcast.id}`}
          className="text-xs font-medium text-orange-600 hover:underline"
        >
          Browse episodes →
        </Link>
        {podcast.website && (
          <a
            href={podcast.website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
          >
            <ExternalLink size={11} />
            Website
          </a>
        )}
      </div>
    </div>
  )
}

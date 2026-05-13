export interface SourceChunk {
  chunk_id: string
  episode_id: string
  podcast_name: string
  episode_title: string
  published_at: string | null
  excerpt: string
  start_secs: number | null
  similarity: number
  timestamp_str?: string | null
}

export interface SearchResponse {
  answer: string
  sources: SourceChunk[]
  query: string
}

export interface Podcast {
  id: string
  name: string
  description: string | null
  cover_image: string | null
  website: string | null
}

export interface Episode {
  id: string
  podcast_id: string
  podcast_name: string | null
  title: string
  published_at: string | null
  duration_secs: number | null
  status: string
}

export interface Stats {
  podcasts: number
  episodes_indexed: number
  chunks: number
}

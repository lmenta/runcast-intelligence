import { Episode, Podcast, SearchResponse, Stats } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

export async function search(query: string, limit = 10): Promise<SearchResponse> {
  return apiFetch('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit }),
  })
}

export async function getPodcasts(): Promise<Podcast[]> {
  return apiFetch('/api/podcasts')
}

export async function getEpisodes(params?: {
  podcast_id?: string
  status?: string
  limit?: number
  offset?: number
}): Promise<Episode[]> {
  const qs = new URLSearchParams()
  if (params?.podcast_id) qs.set('podcast_id', params.podcast_id)
  if (params?.status) qs.set('status', params.status)
  if (params?.limit) qs.set('limit', String(params.limit))
  if (params?.offset) qs.set('offset', String(params.offset))
  return apiFetch(`/api/episodes?${qs}`)
}

export async function getStats(): Promise<Stats> {
  return apiFetch('/api/stats')
}

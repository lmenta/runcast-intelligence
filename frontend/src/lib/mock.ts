/**
 * Mock data for local UI development without a running backend.
 * Used when NEXT_PUBLIC_USE_MOCK=true
 */

import { Episode, Podcast, SearchResponse, Stats } from './types'

export const mockStats: Stats = {
  podcasts: 9,
  episodes_indexed: 42,
  chunks: 3218,
}

export const mockPodcasts: Podcast[] = [
  { id: '1', name: 'The Strength Running Podcast', description: 'Jason Fitzgerald on training smarter, avoiding injury, and running faster.', cover_image: null, website: 'https://strengthrunning.com' },
  { id: '2', name: 'Ali on the Run Show', description: 'Interviews with runners of all kinds — elites, everyday athletes, coaches, and creatives.', cover_image: null, website: 'https://aliontherun.com' },
  { id: '3', name: 'The Morning Shakeout Podcast', description: 'Mario Fraioli interviews runners, coaches, writers, and thinkers at the intersection of running and life.', cover_image: null, website: 'https://themorningshakeout.com' },
  { id: '4', name: 'Run to the Top', description: 'Expert training advice and science-based coaching from Runners Connect.', cover_image: null, website: 'https://runnersconnect.net' },
  { id: '5', name: 'The Running Explained Podcast', description: 'Science-based running coaching for everyday runners.', cover_image: null, website: 'https://runningexplained.com' },
  { id: '6', name: 'Some Work, All Play', description: 'David and Megan Roche on trail running, coaching philosophy, and the joy of sport.', cover_image: null, website: 'https://davidroche.run' },
  { id: '7', name: 'The CITIUS MAG Podcast', description: 'Track, field, and road racing news, analysis, and interviews.', cover_image: null, website: 'https://citiusmag.com' },
  { id: '8', name: 'The Planted Runner', description: 'Plant-based nutrition and running performance.', cover_image: null, website: 'https://theplantedrunner.com' },
  { id: '9', name: 'Real Talk Running', description: 'Honest conversations about running, training, and racing.', cover_image: null, website: null },
]

export const mockEpisodes: Episode[] = [
  { id: 'e1', podcast_id: '1', podcast_name: 'The Strength Running Podcast', title: 'How a Psychotherapist Coaches Elite Runners', published_at: '2025-04-15T00:00:00Z', duration_secs: 3420, status: 'ready' },
  { id: 'e2', podcast_id: '2', podcast_name: 'Ali on the Run Show', title: '884. A May Message from Ali', published_at: '2025-05-01T00:00:00Z', duration_secs: 1800, status: 'ready' },
  { id: 'e3', podcast_id: '3', podcast_name: 'The Morning Shakeout Podcast', title: 'Episode 251 | Matt Taylor on Brand Building, Storytelling, and Running', published_at: '2025-04-20T00:00:00Z', duration_secs: 4200, status: 'ready' },
  { id: 'e4', podcast_id: '4', podcast_name: 'Run to the Top', title: 'Learning From Injury Setbacks to Run Smarter & Faster', published_at: '2025-04-28T00:00:00Z', duration_secs: 3600, status: 'ready' },
  { id: 'e5', podcast_id: '5', podcast_name: 'The Running Explained Podcast', title: 'ADHD, Anxiety, and Running: What No One Talks About', published_at: '2025-05-02T00:00:00Z', duration_secs: 2700, status: 'ready' },
  { id: 'e6', podcast_id: '6', podcast_name: 'Some Work, All Play', title: '310. The Fatigue Resistance Episode! Rachel Entrekin Makes History', published_at: '2025-04-22T00:00:00Z', duration_secs: 3900, status: 'pending' },
]

export const mockSearchResponse: SearchResponse = {
  query: 'how do elites taper for a marathon?',
  answer: `Based on multiple podcast discussions, elite marathon tapering typically follows a 2–3 week protocol with very specific principles.

**The key phases:**
- **Week 3 out**: Drop volume by ~20–30%, keep intensity. Long run shortens to 14–16 miles but pace stays honest.
- **Week 2 out**: Volume drops another 20%. Key workouts include race-pace miles (8–10 miles total at goal pace). Jason Fitzgerald emphasises that "the hay is in the barn" — fitness doesn't improve here, but fatigue does clear.
- **Final week**: Mostly easy running, 2–3 short strides daily to keep the legs sharp. Many elites do a short 3–4 mile shakeout with 4×100m strides two days before.

**What separates elite tapering from recreational runners:** Elites maintain higher intensity throughout the taper but cut volume aggressively. Recreational runners often make the mistake of cutting both — which leaves them feeling flat on race day.`,
  sources: [
    { chunk_id: 'c1', episode_id: 'e1', podcast_name: 'The Strength Running Podcast', episode_title: 'How to Peak for a Marathon', published_at: '2024-09-12T00:00:00Z', excerpt: 'The taper is not about resting — it\'s about converting fatigue into freshness while keeping your fitness intact. Most runners cut too much intensity in the final two weeks...', start_secs: 1420, similarity: 0.91 },
    { chunk_id: 'c2', episode_id: 'e3', podcast_name: 'The Morning Shakeout Podcast', episode_title: 'Episode 218 | Stephanie Bruce on Marathon Preparation', published_at: '2024-08-05T00:00:00Z', excerpt: 'In the last week I\'m still doing strides, I\'m still doing a couple of pickups. I want my legs to remember what fast feels like going into race day...', start_secs: 2150, similarity: 0.87 },
    { chunk_id: 'c3', episode_id: 'e4', podcast_name: 'Run to the Top', episode_title: 'Science of Marathon Peaking with Dr. Kipchoge', published_at: '2024-10-18T00:00:00Z', excerpt: 'Research shows that a 2-week taper for marathon is optimal for most trained runners. The volume reduction should be 40-60% while keeping intensity...', start_secs: 890, similarity: 0.84 },
  ],
}

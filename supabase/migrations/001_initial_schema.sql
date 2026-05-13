-- Enable pgvector
create extension if not exists vector;

-- Podcasts registry
create table podcasts (
    id          uuid primary key default gen_random_uuid(),
    name        text not null,
    rss_url     text not null unique,
    website     text,
    description text,
    cover_image text,
    language    text default 'en',
    active      boolean default true,
    created_at  timestamptz default now()
);

-- Episodes
create table episodes (
    id              uuid primary key default gen_random_uuid(),
    podcast_id      uuid not null references podcasts(id) on delete cascade,
    guid            text not null unique,          -- RSS guid, prevents duplicates
    title           text not null,
    description     text,
    published_at    timestamptz,
    duration_secs   int,
    audio_url       text not null,
    episode_number  int,
    season_number   int,
    status          text default 'pending'         -- pending | transcribing | embedding | ready | failed
        check (status in ('pending','transcribing','embedding','ready','failed')),
    error_msg       text,
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

create index episodes_podcast_id_idx on episodes(podcast_id);
create index episodes_status_idx on episodes(status);
create index episodes_published_at_idx on episodes(published_at desc);

-- Transcript chunks + embeddings
create table chunks (
    id          uuid primary key default gen_random_uuid(),
    episode_id  uuid not null references episodes(id) on delete cascade,
    content     text not null,
    start_secs  float,           -- timestamp in the episode
    end_secs    float,
    chunk_index int not null,
    embedding   vector(1536),    -- OpenAI text-embedding-3-small dimensions
    created_at  timestamptz default now()
);

create index chunks_episode_id_idx on chunks(episode_id);

-- Vector similarity search index (IVFFlat — good up to ~1M rows)
-- Run after loading data: create index chunks_embedding_idx on chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Guests
create table guests (
    id          uuid primary key default gen_random_uuid(),
    name        text not null unique,
    bio         text,
    website     text,
    created_at  timestamptz default now()
);

-- Episode <-> Guest
create table episode_guests (
    episode_id  uuid references episodes(id) on delete cascade,
    guest_id    uuid references guests(id) on delete cascade,
    primary key (episode_id, guest_id)
);

-- Topics (LLM-extracted per episode)
create table topics (
    id      uuid primary key default gen_random_uuid(),
    name    text not null unique
);

create table episode_topics (
    episode_id  uuid references episodes(id) on delete cascade,
    topic_id    uuid references topics(id) on delete cascade,
    primary key (episode_id, topic_id)
);

-- Similarity search function
create or replace function search_chunks(
    query_embedding vector(1536),
    match_count      int default 10,
    min_similarity   float default 0.5
)
returns table (
    chunk_id        uuid,
    episode_id      uuid,
    podcast_name    text,
    episode_title   text,
    published_at    timestamptz,
    content         text,
    start_secs      float,
    similarity      float
)
language sql stable
as $$
    select
        c.id        as chunk_id,
        e.id        as episode_id,
        p.name      as podcast_name,
        e.title     as episode_title,
        e.published_at,
        c.content,
        c.start_secs,
        1 - (c.embedding <=> query_embedding) as similarity
    from chunks c
    join episodes e on c.episode_id = e.id
    join podcasts p on e.podcast_id = p.id
    where e.status = 'ready'
      and 1 - (c.embedding <=> query_embedding) > min_similarity
    order by c.embedding <=> query_embedding
    limit match_count;
$$;

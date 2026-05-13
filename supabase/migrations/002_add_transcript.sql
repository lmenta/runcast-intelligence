-- Add transcript text storage and expand status values
alter table episodes add column if not exists transcript text;

-- Expand status to include transcribed/embedding steps
alter table episodes drop constraint if exists episodes_status_check;
alter table episodes add constraint episodes_status_check
    check (status in ('pending', 'transcribing', 'transcribed', 'embedding', 'ready', 'failed'));

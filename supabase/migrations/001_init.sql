-- EmpowerHer — run in Supabase SQL editor or via CLI migrations
-- Enable UUID generation
create extension if not exists "pgcrypto";

create table if not exists public.mentors (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  title text not null,
  bio text,
  expertise text[] default '{}',
  industry_tags text[] default '{}',
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  company text not null,
  location text,
  employment_type text default 'Full-time',
  summary text,
  skill_tags text[] default '{}',
  industry text,
  is_open boolean not null default true,
  created_at timestamptz not null default now()
);

-- Optional: mentee intake log (for analytics / future personalization)
create table if not exists public.match_requests (
  id uuid primary key default gen_random_uuid(),
  message text not null,
  created_at timestamptz not null default now()
);

alter table public.mentors enable row level security;
alter table public.jobs enable row level security;
alter table public.match_requests enable row level security;

-- Public read for mentors and jobs (tighten for production)
create policy "Mentors are viewable by everyone"
  on public.mentors for select using (true);

create policy "Jobs are viewable by everyone"
  on public.jobs for select using (true);

-- Service role bypasses RLS; anon users can read mentors/jobs via above policies
-- For inserts from backend only, use service_role key and omit insert policies for anon

-- Seed examples (optional)
insert into public.mentors (name, title, bio, expertise, industry_tags)
values
  (
    'Aisha Okonkwo',
    'Director of UX Research, Health Tech',
    'Former clinician turned researcher; mentors career pivots and portfolio reviews.',
    array['ux research','health tech','career pivot','interviews'],
    array['healthcare','saas']
  ),
  (
    'Marina Volkov',
    'Staff Backend Engineer',
    'Backend, distributed systems, and interview loops at product companies.',
    array['backend','python','system design','new grad'],
    array['fintech','enterprise']
  ),
  (
    'Priya Desai',
    'Group PM, Fintech',
    'Returned from parental leave; focuses on flexible remote paths for PMs.',
    array['product management','fintech','remote work','parental leave'],
    array['fintech']
  )
;

insert into public.jobs (title, company, location, employment_type, summary, skill_tags, industry)
values
  (
    'UX Researcher II',
    'Northwind Health',
    'Remote (US)',
    'Full-time',
    'Mixed-methods studies for clinician workflows; cross-functional with design and PM.',
    array['ux research','healthcare','mixed methods'],
    'health tech'
  ),
  (
    'Backend Engineer',
    'Riverbank Labs',
    'Hybrid · NYC',
    'Full-time',
    'Python services, event-driven architecture, mentoring interns.',
    array['python','backend','distributed systems'],
    'saas'
  ),
  (
    'Senior Product Manager',
    'Cedar Payments',
    'Remote',
    'Full-time',
    'Payments roadmap; partner with compliance and design on customer journeys.',
    array['product management','fintech','remote'],
    'fintech'
  )
;

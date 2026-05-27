create extension if not exists "uuid-ossp";

create table if not exists public.k_projects (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  description text,
  status text default 'active',
  created_at timestamptz default now()
);

create table if not exists public.k_memories (
  id uuid primary key default uuid_generate_v4(),
  category text,
  title text not null,
  content text not null,
  source text default 'manual',
  created_at timestamptz default now()
);

create table if not exists public.k_tasks (
  id uuid primary key default uuid_generate_v4(),
  project_id uuid references public.k_projects(id) on delete cascade,
  title text not null,
  instruction text,
  status text default 'pending',
  risk_level text default 'low',
  requires_approval boolean default false,
  approved boolean default false,
  result text,
  created_at timestamptz default now(),
  executed_at timestamptz
);

create table if not exists public.k_reports (
  id uuid primary key default uuid_generate_v4(),
  project_id uuid references public.k_projects(id) on delete cascade,
  title text,
  content text,
  created_at timestamptz default now()
);

create table if not exists public.k_connectors (
  id uuid primary key default uuid_generate_v4(),
  connector_name text unique,
  enabled boolean default false,
  last_sync timestamptz,
  created_at timestamptz default now()
);

create table if not exists public.k_approvals (
  id uuid primary key default uuid_generate_v4(),
  task_id uuid references public.k_tasks(id) on delete cascade,
  approved boolean default false,
  approved_by text,
  created_at timestamptz default now()
);

create table if not exists public.k_agent_logs (
  id uuid primary key default uuid_generate_v4(),
  agent text,
  action text,
  details text,
  created_at timestamptz default now()
);

alter table public.k_projects enable row level security;
alter table public.k_memories enable row level security;
alter table public.k_tasks enable row level security;
alter table public.k_reports enable row level security;
alter table public.k_connectors enable row level security;
alter table public.k_approvals enable row level security;
alter table public.k_agent_logs enable row level security;

create policy "enable all for anon"
on public.k_projects
for all
using (true);

create policy "enable all for anon memories"
on public.k_memories
for all
using (true);

create policy "enable all for anon tasks"
on public.k_tasks
for all
using (true);

create policy "enable all for anon reports"
on public.k_reports
for all
using (true);

create policy "enable all for anon connectors"
on public.k_connectors
for all
using (true);

create policy "enable all for anon approvals"
on public.k_approvals
for all
using (true);

create policy "enable all for anon logs"
on public.k_agent_logs
for all
using (true);
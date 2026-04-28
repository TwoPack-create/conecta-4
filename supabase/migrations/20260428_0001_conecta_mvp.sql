-- Conecta FCFM MVP schema for Supabase (PostgreSQL)
-- Multi-tenant ready via campus_id and strict RLS by tenant.

begin;

create extension if not exists pgcrypto;
create extension if not exists citext;

-- =========================================================
-- ENUMS
-- =========================================================
create type public.trip_mode as enum ('transporte_publico', 'vehiculo');
create type public.trip_status as enum ('borrador', 'publicado', 'en_curso', 'completado', 'cancelado');
create type public.public_transport_mode as enum ('metro', 'micro', 'a_pie');
create type public.trip_participant_role as enum ('creador', 'pasajero', 'acompanante');
create type public.report_type as enum ('ruta_segura', 'ruta_insegura', 'incidente');
create type public.risk_level as enum ('bajo', 'medio', 'alto');
create type public.accompaniment_status as enum ('activo', 'expirado', 'confirmado', 'cancelado');
create type public.alert_target_type as enum ('contactos_externos', 'usuarios_in_app', 'grupo_in_app');
create type public.wallet_entry_type as enum ('recarga', 'reserva', 'liberacion', 'pago_viaje', 'comision_plataforma', 'ajuste', 'reembolso');
create type public.sos_event_type as enum ('sos_manual', 'acompaname_expirado');

-- =========================================================
-- CORE MULTI-TENANT TABLES
-- =========================================================
create table public.campuses (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  email citext not null unique,
  full_name text,
  avatar_url text,
  phone text,
  is_admin boolean not null default false,
  is_profile_complete boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint users_email_domain_chk check (
    lower(split_part(email::text, '@', 2)) in ('ug.uchile.cl', 'ing.uchile.cl', 'uchile.cl', 'idiem.cl')
  )
);

create table public.emergency_contacts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  contact_name text not null,
  phone text not null,
  relationship text,
  created_at timestamptz not null default now(),
  unique (user_id, phone)
);

create table public.emergency_groups (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  created_by uuid not null references public.users(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now()
);

create table public.emergency_group_members (
  group_id uuid not null references public.emergency_groups(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  created_at timestamptz not null default now(),
  primary key (group_id, user_id)
);

create table public.user_wallets (
  user_id uuid primary key references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  balance_available numeric(12,2) not null default 0,
  balance_reserved numeric(12,2) not null default 0,
  updated_at timestamptz not null default now(),
  constraint wallet_balance_non_negative_chk check (
    balance_available >= 0 and balance_reserved >= 0
  )
);

create table public.wallet_ledger (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  user_id uuid not null references public.users(id) on delete cascade,
  trip_id uuid,
  entry_type public.wallet_entry_type not null,
  amount numeric(12,2) not null,
  currency char(3) not null default 'CLP',
  external_reference text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- =========================================================
-- TRIPS + PARTICIPATION + CHAT + RATINGS
-- =========================================================
create table public.trips (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  creator_id uuid not null references public.users(id) on delete cascade,
  mode public.trip_mode not null,
  status public.trip_status not null default 'publicado',
  starts_at timestamptz not null,
  estimated_arrival_at timestamptz,
  origin_label text not null,
  destination_label text not null,
  origin_lat numeric(9,6),
  origin_lng numeric(9,6),
  destination_lat numeric(9,6),
  destination_lng numeric(9,6),
  route_description text,
  route_polyline text,
  seats_total int not null,
  seats_available int not null,
  public_transport_mode public.public_transport_mode,
  line_or_route text,
  direction text,
  vehicle_name text,
  vehicle_model text,
  vehicle_type text,
  vehicle_color text,
  license_plate text,
  costo_compartido numeric(12,2) not null default 0,
  comision_plataforma numeric(12,2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint trips_seats_min_chk check (seats_total >= 3),
  constraint trips_seats_available_chk check (seats_available >= 0 and seats_available <= seats_total),
  constraint trips_mode_transport_chk check (
    (mode = 'transporte_publico' and public_transport_mode is not null)
    or (mode = 'vehiculo')
  ),
  constraint trips_mode_cost_chk check (
    (mode = 'vehiculo' and costo_compartido >= 0 and comision_plataforma >= 0)
    or (mode = 'transporte_publico' and costo_compartido = 0)
  )
);

alter table public.wallet_ledger
  add constraint wallet_ledger_trip_fk
  foreign key (trip_id) references public.trips(id) on delete set null;

create table public.trip_participants (
  trip_id uuid not null references public.trips(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  role public.trip_participant_role not null default 'pasajero',
  joined_at timestamptz not null default now(),
  left_at timestamptz,
  primary key (trip_id, user_id)
);

create table public.trip_messages (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  sender_id uuid not null references public.users(id) on delete cascade,
  message text not null,
  created_at timestamptz not null default now()
);

create table public.trip_ratings (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  trip_id uuid not null references public.trips(id) on delete cascade,
  rater_user_id uuid not null references public.users(id) on delete cascade,
  rated_user_id uuid not null references public.users(id) on delete cascade,
  calificacion_general smallint not null check (calificacion_general between 1 and 5),
  puntualidad smallint not null check (puntualidad between 1 and 5),
  ambiente smallint not null check (ambiente between 1 and 5),
  seguridad smallint not null check (seguridad between 1 and 5),
  comment text,
  created_at timestamptz not null default now(),
  unique (trip_id, rater_user_id, rated_user_id),
  constraint ratings_distinct_users_chk check (rater_user_id <> rated_user_id)
);

-- =========================================================
-- ROUTES REPORTS + BLIPS + VOTES
-- =========================================================
create table public.route_reports (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  created_by uuid not null references public.users(id) on delete cascade,
  report_type public.report_type not null,
  risk_level public.risk_level not null,
  location_label text not null,
  lat numeric(9,6),
  lng numeric(9,6),
  incident_at timestamptz,
  description text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.report_votes (
  report_id uuid not null references public.route_reports(id) on delete cascade,
  voter_user_id uuid not null references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  vote smallint not null check (vote in (-1, 1)),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (report_id, voter_user_id)
);

create table public.blips (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  created_by uuid not null references public.users(id) on delete cascade,
  report_id uuid references public.route_reports(id) on delete set null,
  lat numeric(9,6) not null,
  lng numeric(9,6) not null,
  message text,
  is_high_priority boolean not null default false,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '24 hours')
);

-- =========================================================
-- SAFETY (ACOMPANAME + SOS + LOCATION HISTORY)
-- =========================================================
create table public.accompaniment_sessions (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  user_id uuid not null references public.users(id) on delete cascade,
  trip_id uuid references public.trips(id) on delete set null,
  status public.accompaniment_status not null default 'activo',
  target_type public.alert_target_type not null,
  expected_arrival_at timestamptz not null,
  grace_minutes int not null default 15 check (grace_minutes >= 0),
  last_lat numeric(9,6),
  last_lng numeric(9,6),
  started_at timestamptz not null default now(),
  expired_at timestamptz,
  confirmed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.accompaniment_recipients (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.accompaniment_sessions(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  recipient_user_id uuid references public.users(id) on delete cascade,
  recipient_contact_id uuid references public.emergency_contacts(id) on delete cascade,
  recipient_group_id uuid references public.emergency_groups(id) on delete cascade,
  created_at timestamptz not null default now(),
  constraint accompaniment_single_target_chk check (
    ((recipient_user_id is not null)::int + (recipient_contact_id is not null)::int + (recipient_group_id is not null)::int) = 1
  )
);

create table public.location_history (
  id bigserial primary key,
  campus_id uuid not null references public.campuses(id),
  user_id uuid references public.users(id) on delete set null,
  accompaniment_session_id uuid references public.accompaniment_sessions(id) on delete set null,
  source text not null default 'acompaname',
  lat numeric(9,6) not null,
  lng numeric(9,6) not null,
  created_at timestamptz not null default now(),
  anonymized_at timestamptz
);

create table public.sos_events (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  user_id uuid not null references public.users(id) on delete cascade,
  accompaniment_session_id uuid references public.accompaniment_sessions(id) on delete set null,
  event_type public.sos_event_type not null,
  lat numeric(9,6),
  lng numeric(9,6),
  created_at timestamptz not null default now()
);

-- =========================================================
-- TRIGGERS / FUNCTIONS
-- =========================================================
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger users_set_updated_at
before update on public.users
for each row execute function public.set_updated_at();

create trigger trips_set_updated_at
before update on public.trips
for each row execute function public.set_updated_at();

create trigger route_reports_set_updated_at
before update on public.route_reports
for each row execute function public.set_updated_at();

create trigger report_votes_set_updated_at
before update on public.report_votes
for each row execute function public.set_updated_at();

create trigger accompaniment_sessions_set_updated_at
before update on public.accompaniment_sessions
for each row execute function public.set_updated_at();

create or replace function public.enforce_emergency_contacts_limit()
returns trigger
language plpgsql
as $$
declare
  v_count int;
begin
  select count(*) into v_count from public.emergency_contacts where user_id = new.user_id;
  if tg_op = 'INSERT' and v_count >= 3 then
    raise exception 'Máximo 3 contactos de emergencia por usuario';
  end if;
  return new;
end;
$$;

create trigger emergency_contacts_limit_trg
before insert on public.emergency_contacts
for each row execute function public.enforce_emergency_contacts_limit();

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_email text;
  v_domain text;
  v_default_campus uuid;
begin
  v_email := coalesce(new.email, '');
  v_domain := lower(split_part(v_email, '@', 2));

  if v_domain not in ('ug.uchile.cl', 'ing.uchile.cl', 'uchile.cl', 'idiem.cl') then
    raise exception 'Dominio no permitido para Conecta FCFM';
  end if;

  select id into v_default_campus
  from public.campuses
  where code = 'fcfm'
  limit 1;

  if v_default_campus is null then
    raise exception 'No existe campus por defecto (code=fcfm)';
  end if;

  insert into public.users (id, campus_id, email, full_name, avatar_url)
  values (
    new.id,
    v_default_campus,
    v_email,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name'),
    new.raw_user_meta_data ->> 'avatar_url'
  );

  insert into public.user_wallets (user_id, campus_id) values (new.id, v_default_campus);

  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_auth_user();

create or replace function public.current_user_campus_id()
returns uuid
language sql
stable
as $$
  select u.campus_id
  from public.users u
  where u.id = auth.uid();
$$;

create or replace function public.is_current_user_admin()
returns boolean
language sql
stable
as $$
  select coalesce((select is_admin from public.users where id = auth.uid()), false);
$$;

-- job helper: anonymize location history older than 30 days.
create or replace function public.anonymize_old_location_history()
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  v_count bigint;
begin
  update public.location_history
  set user_id = null,
      anonymized_at = now()
  where user_id is not null
    and created_at < now() - interval '30 days';

  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

-- =========================================================
-- INDEXES
-- =========================================================
create index users_campus_idx on public.users(campus_id);

create index emergency_contacts_user_idx on public.emergency_contacts(user_id);
create index emergency_groups_campus_idx on public.emergency_groups(campus_id);
create index emergency_group_members_user_idx on public.emergency_group_members(user_id);

create index trips_campus_status_starts_idx on public.trips(campus_id, status, starts_at);
create index trips_creator_idx on public.trips(creator_id);
create index trip_participants_user_idx on public.trip_participants(user_id);
create index trip_messages_trip_created_idx on public.trip_messages(trip_id, created_at);
create index trip_ratings_trip_idx on public.trip_ratings(trip_id);
create index trip_ratings_rated_user_idx on public.trip_ratings(rated_user_id);

create index route_reports_campus_created_idx on public.route_reports(campus_id, created_at desc);
create index report_votes_report_idx on public.report_votes(report_id);
create index blips_campus_expires_idx on public.blips(campus_id, expires_at);

create index accompaniment_sessions_user_status_idx on public.accompaniment_sessions(user_id, status);
create index accompaniment_recipients_session_idx on public.accompaniment_recipients(session_id);
create index location_history_session_created_idx on public.location_history(accompaniment_session_id, created_at);
create index location_history_created_idx on public.location_history(created_at);
create index sos_events_user_created_idx on public.sos_events(user_id, created_at);

create index wallet_ledger_user_created_idx on public.wallet_ledger(user_id, created_at);

-- =========================================================
-- RLS
-- =========================================================
alter table public.campuses enable row level security;
alter table public.users enable row level security;
alter table public.emergency_contacts enable row level security;
alter table public.emergency_groups enable row level security;
alter table public.emergency_group_members enable row level security;
alter table public.user_wallets enable row level security;
alter table public.wallet_ledger enable row level security;
alter table public.trips enable row level security;
alter table public.trip_participants enable row level security;
alter table public.trip_messages enable row level security;
alter table public.trip_ratings enable row level security;
alter table public.route_reports enable row level security;
alter table public.report_votes enable row level security;
alter table public.blips enable row level security;
alter table public.accompaniment_sessions enable row level security;
alter table public.accompaniment_recipients enable row level security;
alter table public.location_history enable row level security;
alter table public.sos_events enable row level security;

-- campuses (read same tenant; writes admin only)
create policy campuses_select_same_tenant on public.campuses
for select to authenticated
using (id = public.current_user_campus_id());

create policy campuses_admin_write on public.campuses
for all to authenticated
using (public.is_current_user_admin())
with check (public.is_current_user_admin());

-- users
create policy users_select_same_campus on public.users
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy users_insert_self_or_admin on public.users
for insert to authenticated
with check (
  (id = auth.uid() and campus_id = public.current_user_campus_id())
  or public.is_current_user_admin()
);

create policy users_update_self_or_admin on public.users
for update to authenticated
using (id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy users_delete_admin on public.users
for delete to authenticated
using (public.is_current_user_admin());

-- emergency_contacts
create policy emergency_contacts_select_same_campus on public.emergency_contacts
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy emergency_contacts_write_owner_or_admin on public.emergency_contacts
for all to authenticated
using (user_id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id() and (user_id = auth.uid() or public.is_current_user_admin()));

-- emergency groups/members
create policy emergency_groups_select_same_campus on public.emergency_groups
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy emergency_groups_write_creator_or_admin on public.emergency_groups
for all to authenticated
using (created_by = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id() and (created_by = auth.uid() or public.is_current_user_admin()));

create policy emergency_group_members_select_same_campus on public.emergency_group_members
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy emergency_group_members_write_admin_or_group_creator on public.emergency_group_members
for all to authenticated
using (
  public.is_current_user_admin()
  or exists (
    select 1 from public.emergency_groups g
    where g.id = emergency_group_members.group_id and g.created_by = auth.uid()
  )
)
with check (campus_id = public.current_user_campus_id());

-- wallets
create policy wallets_select_owner_or_admin on public.user_wallets
for select to authenticated
using (user_id = auth.uid() or public.is_current_user_admin());

create policy wallets_update_admin_only on public.user_wallets
for update to authenticated
using (public.is_current_user_admin())
with check (public.is_current_user_admin());

create policy wallet_ledger_select_owner_or_admin on public.wallet_ledger
for select to authenticated
using ((user_id = auth.uid() or public.is_current_user_admin()) and campus_id = public.current_user_campus_id());

create policy wallet_ledger_insert_admin_only on public.wallet_ledger
for insert to authenticated
with check (public.is_current_user_admin() and campus_id = public.current_user_campus_id());

-- trips
create policy trips_select_same_campus on public.trips
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy trips_insert_same_campus on public.trips
for insert to authenticated
with check (creator_id = auth.uid() and campus_id = public.current_user_campus_id());

create policy trips_update_creator_or_admin on public.trips
for update to authenticated
using (creator_id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy trips_delete_creator_or_admin on public.trips
for delete to authenticated
using (creator_id = auth.uid() or public.is_current_user_admin());

-- trip participants
create policy trip_participants_select_same_campus on public.trip_participants
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy trip_participants_insert_self_or_creator_or_admin on public.trip_participants
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (
    user_id = auth.uid()
    or public.is_current_user_admin()
    or exists (select 1 from public.trips t where t.id = trip_id and t.creator_id = auth.uid())
  )
);

create policy trip_participants_delete_self_or_creator_or_admin on public.trip_participants
for delete to authenticated
using (
  user_id = auth.uid()
  or public.is_current_user_admin()
  or exists (select 1 from public.trips t where t.id = trip_id and t.creator_id = auth.uid())
);

-- trip messages
create policy trip_messages_select_same_campus on public.trip_messages
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy trip_messages_insert_members_only on public.trip_messages
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and sender_id = auth.uid()
  and exists (
    select 1 from public.trip_participants tp
    where tp.trip_id = trip_messages.trip_id
      and tp.user_id = auth.uid()
  )
);

create policy trip_messages_delete_sender_or_admin on public.trip_messages
for delete to authenticated
using (sender_id = auth.uid() or public.is_current_user_admin());

-- ratings
create policy trip_ratings_select_same_campus on public.trip_ratings
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy trip_ratings_insert_rater_or_admin on public.trip_ratings
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (rater_user_id = auth.uid() or public.is_current_user_admin())
);

create policy trip_ratings_update_admin_only on public.trip_ratings
for update to authenticated
using (public.is_current_user_admin())
with check (public.is_current_user_admin());

-- route reports
create policy route_reports_select_same_campus on public.route_reports
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy route_reports_insert_creator on public.route_reports
for insert to authenticated
with check (created_by = auth.uid() and campus_id = public.current_user_campus_id());

create policy route_reports_update_creator_or_admin on public.route_reports
for update to authenticated
using (created_by = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy route_reports_delete_creator_or_admin on public.route_reports
for delete to authenticated
using (created_by = auth.uid() or public.is_current_user_admin());

-- report votes
create policy report_votes_select_same_campus on public.report_votes
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy report_votes_insert_self on public.report_votes
for insert to authenticated
with check (voter_user_id = auth.uid() and campus_id = public.current_user_campus_id());

create policy report_votes_update_self_or_admin on public.report_votes
for update to authenticated
using (voter_user_id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy report_votes_delete_self_or_admin on public.report_votes
for delete to authenticated
using (voter_user_id = auth.uid() or public.is_current_user_admin());

-- blips
create policy blips_select_same_campus on public.blips
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy blips_insert_creator on public.blips
for insert to authenticated
with check (created_by = auth.uid() and campus_id = public.current_user_campus_id());

create policy blips_update_creator_or_admin on public.blips
for update to authenticated
using (created_by = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy blips_delete_creator_or_admin on public.blips
for delete to authenticated
using (created_by = auth.uid() or public.is_current_user_admin());

-- accompaniment sessions + recipients + location history + sos
create policy accompaniment_sessions_select_same_campus on public.accompaniment_sessions
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy accompaniment_sessions_insert_owner on public.accompaniment_sessions
for insert to authenticated
with check (user_id = auth.uid() and campus_id = public.current_user_campus_id());

create policy accompaniment_sessions_update_owner_or_admin on public.accompaniment_sessions
for update to authenticated
using (user_id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy accompaniment_sessions_delete_owner_or_admin on public.accompaniment_sessions
for delete to authenticated
using (user_id = auth.uid() or public.is_current_user_admin());

create policy accompaniment_recipients_select_same_campus on public.accompaniment_recipients
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy accompaniment_recipients_write_owner_or_admin on public.accompaniment_recipients
for all to authenticated
using (
  public.is_current_user_admin()
  or exists (
    select 1 from public.accompaniment_sessions s
    where s.id = accompaniment_recipients.session_id and s.user_id = auth.uid()
  )
)
with check (campus_id = public.current_user_campus_id());

create policy location_history_select_same_campus on public.location_history
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy location_history_insert_owner_or_admin on public.location_history
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (
    public.is_current_user_admin()
    or user_id = auth.uid()
  )
);

create policy location_history_update_admin_only on public.location_history
for update to authenticated
using (public.is_current_user_admin())
with check (public.is_current_user_admin());

create policy sos_events_select_same_campus on public.sos_events
for select to authenticated
using (campus_id = public.current_user_campus_id());

create policy sos_events_insert_owner_or_admin on public.sos_events
for insert to authenticated
with check (campus_id = public.current_user_campus_id() and (user_id = auth.uid() or public.is_current_user_admin()));

create policy sos_events_delete_admin_only on public.sos_events
for delete to authenticated
using (public.is_current_user_admin());

-- =========================================================
-- BOOTSTRAP DEFAULT CAMPUS FOR MVP
-- =========================================================
insert into public.campuses (code, name)
values ('fcfm', 'FCFM - Universidad de Chile')
on conflict (code) do nothing;

commit;

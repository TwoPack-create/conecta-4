begin;

-- Allow unlimited capacity for organizational (free) public transport trips.
alter table public.trips
  add column if not exists is_unlimited_capacity boolean not null default false;

alter table public.trips
  alter column seats_total drop not null,
  alter column seats_available drop not null;

alter table public.trips drop constraint if exists trips_seats_min_chk;
alter table public.trips drop constraint if exists trips_seats_available_chk;

alter table public.trips
  add constraint trips_capacity_chk
  check (
    (is_unlimited_capacity = true and seats_total is null and seats_available is null)
    or
    (is_unlimited_capacity = false and seats_total >= 3 and seats_available >= 0 and seats_available <= seats_total)
  );

create index if not exists trips_capacity_mode_idx on public.trips(campus_id, mode, is_unlimited_capacity);

-- New status for dead-man switch detonation.
do $$
begin
  alter type public.accompaniment_status add value if not exists 'alerta_detonada';
exception
  when duplicate_object then null;
end$$;

commit;

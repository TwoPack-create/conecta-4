begin;

alter table public.trip_participants
  add column if not exists status text not null default 'pendiente';

create index if not exists trip_participants_trip_status_idx on public.trip_participants(trip_id, status);

commit;

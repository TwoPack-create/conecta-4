begin;

alter table public.trips
  add column if not exists acepta_encargos boolean not null default false;

create index if not exists trips_acepta_encargos_idx on public.trips(campus_id, acepta_encargos);

commit;

begin;

alter table public.users
  add column if not exists sos_primary_number text not null default '133';

commit;

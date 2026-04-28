begin;

alter table public.users
  drop column if exists sos_primary_number;

drop policy if exists users_update_self_or_admin on public.users;
create policy users_update_self_or_admin on public.users
for update to authenticated
using (id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

commit;

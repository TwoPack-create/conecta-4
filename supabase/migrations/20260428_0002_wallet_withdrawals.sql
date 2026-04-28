-- Conecta FCFM MVP - wallet settlement, private bank accounts and withdrawal requests

begin;

-- =========================================================
-- NEW ENUMS
-- =========================================================
do $$
begin
  if not exists (select 1 from pg_type where typname = 'trip_payment_status') then
    create type public.trip_payment_status as enum ('retenido', 'acreditado', 'reembolsado', 'cancelado');
  end if;

  if not exists (select 1 from pg_type where typname = 'withdrawal_status') then
    create type public.withdrawal_status as enum ('solicitado', 'aprobado', 'rechazado', 'pagado', 'cancelado');
  end if;
end$$;

-- Extend wallet ledger entries for retention/settlement/payout lifecycle.
do $$
begin
  if exists (select 1 from pg_type where typname = 'wallet_entry_type') then
    begin
      alter type public.wallet_entry_type add value if not exists 'retencion_pago';
      alter type public.wallet_entry_type add value if not exists 'acreditacion_conductor';
      alter type public.wallet_entry_type add value if not exists 'ingreso_comision_plataforma';
      alter type public.wallet_entry_type add value if not exists 'solicitud_retiro';
      alter type public.wallet_entry_type add value if not exists 'retiro_pagado';
      alter type public.wallet_entry_type add value if not exists 'retiro_rechazado';
    exception
      when duplicate_object then null;
    end;
  end if;
end$$;

-- =========================================================
-- PAYMENTS + PRIVATE BANK DATA + WITHDRAWALS
-- =========================================================
create table if not exists public.trip_payments (
  id uuid primary key default gen_random_uuid(),
  campus_id uuid not null references public.campuses(id),
  trip_id uuid not null references public.trips(id) on delete cascade,
  payer_user_id uuid not null references public.users(id) on delete cascade,
  driver_user_id uuid not null references public.users(id) on delete cascade,
  amount_total numeric(12,2) not null check (amount_total >= 0),
  costo_compartido numeric(12,2) not null check (costo_compartido >= 0),
  comision_plataforma numeric(12,2) not null check (comision_plataforma >= 0),
  gateway_provider text,
  gateway_payment_id text,
  gateway_charge_status text,
  status public.trip_payment_status not null default 'retenido',
  retained_at timestamptz not null default now(),
  settled_at timestamptz,
  refunded_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint trip_payments_amount_split_chk check (amount_total = costo_compartido + comision_plataforma),
  constraint trip_payments_unique_payer_per_trip unique (trip_id, payer_user_id)
);

create table if not exists public.user_bank_accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  account_holder_name text not null,
  holder_rut text not null,
  bank_name text not null,
  account_type text not null,
  account_number text not null,
  email_for_payout text,
  is_verified boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.withdrawal_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  campus_id uuid not null references public.campuses(id),
  bank_account_id uuid not null references public.user_bank_accounts(id) on delete restrict,
  amount_requested numeric(12,2) not null check (amount_requested > 0),
  status public.withdrawal_status not null default 'solicitado',
  requested_at timestamptz not null default now(),
  reviewed_at timestamptz,
  processed_at timestamptz,
  reviewer_admin_id uuid references public.users(id) on delete set null,
  external_payout_reference text,
  rejection_reason text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =========================================================
-- HELPERS / TRIGGERS
-- =========================================================
create or replace function public.prevent_trip_payment_settlement_before_trip_completed()
returns trigger
language plpgsql
as $$
declare
  v_trip_status public.trip_status;
begin
  if new.status = 'acreditado' and (old.status is distinct from 'acreditado') then
    select t.status into v_trip_status from public.trips t where t.id = new.trip_id;
    if v_trip_status is distinct from 'completado' then
      raise exception 'No se puede acreditar un pago si el viaje no está completado';
    end if;

    new.settled_at := coalesce(new.settled_at, now());
  end if;

  if new.status = 'reembolsado' and (old.status is distinct from 'reembolsado') then
    new.refunded_at := coalesce(new.refunded_at, now());
  end if;

  new.updated_at := now();
  return new;
end;
$$;

create trigger trip_payments_settlement_guard_trg
before update on public.trip_payments
for each row execute function public.prevent_trip_payment_settlement_before_trip_completed();

create trigger trip_payments_set_updated_at
before update on public.trip_payments
for each row execute function public.set_updated_at();

create trigger user_bank_accounts_set_updated_at
before update on public.user_bank_accounts
for each row execute function public.set_updated_at();

create trigger withdrawal_requests_set_updated_at
before update on public.withdrawal_requests
for each row execute function public.set_updated_at();

create or replace function public.validate_withdrawal_request()
returns trigger
language plpgsql
as $$
declare
  v_wallet public.user_wallets;
  v_owner uuid;
begin
  select user_id into v_owner
  from public.user_bank_accounts
  where id = new.bank_account_id;

  if v_owner is null then
    raise exception 'Cuenta bancaria inválida para retiro';
  end if;

  if v_owner <> new.user_id then
    raise exception 'La cuenta bancaria no pertenece al usuario solicitante';
  end if;

  select * into v_wallet
  from public.user_wallets
  where user_id = new.user_id;

  if v_wallet.user_id is null then
    raise exception 'Billetera no encontrada para el usuario';
  end if;

  if v_wallet.balance_available < new.amount_requested then
    raise exception 'Saldo insuficiente para solicitar retiro';
  end if;

  return new;
end;
$$;

create trigger withdrawal_requests_validate_trg
before insert on public.withdrawal_requests
for each row execute function public.validate_withdrawal_request();

-- =========================================================
-- INDEXES
-- =========================================================
create index if not exists trip_payments_trip_idx on public.trip_payments(trip_id);
create index if not exists trip_payments_payer_idx on public.trip_payments(payer_user_id);
create index if not exists trip_payments_driver_idx on public.trip_payments(driver_user_id);
create index if not exists trip_payments_status_idx on public.trip_payments(status, created_at);

create index if not exists user_bank_accounts_user_idx on public.user_bank_accounts(user_id);
create index if not exists withdrawal_requests_user_status_idx on public.withdrawal_requests(user_id, status, requested_at);
create index if not exists withdrawal_requests_admin_review_idx on public.withdrawal_requests(reviewer_admin_id, reviewed_at);

-- =========================================================
-- RLS
-- =========================================================
alter table public.trip_payments enable row level security;
alter table public.user_bank_accounts enable row level security;
alter table public.withdrawal_requests enable row level security;

-- trip_payments: visibility for payer/driver/admin on same campus.
create policy trip_payments_select_parties_or_admin on public.trip_payments
for select to authenticated
using (
  campus_id = public.current_user_campus_id()
  and (
    payer_user_id = auth.uid()
    or driver_user_id = auth.uid()
    or public.is_current_user_admin()
  )
);

-- insert typically done by backend after gateway callback; allow admin or payer self.
create policy trip_payments_insert_payer_or_admin on public.trip_payments
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (
    payer_user_id = auth.uid()
    or public.is_current_user_admin()
  )
);

create policy trip_payments_update_admin_only on public.trip_payments
for update to authenticated
using (public.is_current_user_admin())
with check (public.is_current_user_admin());

create policy trip_payments_delete_admin_only on public.trip_payments
for delete to authenticated
using (public.is_current_user_admin());

-- user_bank_accounts: private (owner/admin only).
create policy user_bank_accounts_select_owner_or_admin on public.user_bank_accounts
for select to authenticated
using (
  campus_id = public.current_user_campus_id()
  and (user_id = auth.uid() or public.is_current_user_admin())
);

create policy user_bank_accounts_insert_owner_or_admin on public.user_bank_accounts
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (user_id = auth.uid() or public.is_current_user_admin())
);

create policy user_bank_accounts_update_owner_or_admin on public.user_bank_accounts
for update to authenticated
using (user_id = auth.uid() or public.is_current_user_admin())
with check (campus_id = public.current_user_campus_id());

create policy user_bank_accounts_delete_owner_or_admin on public.user_bank_accounts
for delete to authenticated
using (user_id = auth.uid() or public.is_current_user_admin());

-- withdrawals: owner can create/read/cancel own pending requests; admin can review/process.
create policy withdrawal_requests_select_owner_or_admin on public.withdrawal_requests
for select to authenticated
using (
  campus_id = public.current_user_campus_id()
  and (user_id = auth.uid() or public.is_current_user_admin())
);

create policy withdrawal_requests_insert_owner_or_admin on public.withdrawal_requests
for insert to authenticated
with check (
  campus_id = public.current_user_campus_id()
  and (user_id = auth.uid() or public.is_current_user_admin())
);

create policy withdrawal_requests_update_owner_or_admin on public.withdrawal_requests
for update to authenticated
using (
  campus_id = public.current_user_campus_id()
  and (user_id = auth.uid() or public.is_current_user_admin())
)
with check (
  campus_id = public.current_user_campus_id()
  and (
    public.is_current_user_admin()
    or (user_id = auth.uid() and status in ('solicitado', 'cancelado'))
  )
);

create policy withdrawal_requests_delete_admin_only on public.withdrawal_requests
for delete to authenticated
using (public.is_current_user_admin());

commit;

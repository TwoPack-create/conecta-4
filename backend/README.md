# Conecta FCFM Backend (FastAPI)

## Estructura

```text
backend/
  app/
    api/v1/endpoints/
      health.py
      wallet.py
      payments.py
      trips.py
      safety.py
      participation.py
    core/
      config.py
    db/
      session.py
    deps/
      auth.py
    models/
      base.py
      wallet.py
      payment.py
      trip.py
      safety.py
      participant.py
      rating.py
    schemas/
      common.py
      wallet.py
      payments.py
      trips.py
      safety.py
      participation.py
      settlement.py
      ratings.py
    services/
      wallet_service.py
      payment_service.py
      trip_service.py
      safety_service.py
      participation_service.py
    workers/
      accompaniment_monitor.py
    main.py
  requirements.txt
  .env.example
```

## Levantar local

1. Crear entorno virtual e instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Copiar variables:

```bash
cp .env.example .env
```

3. Ejecutar servidor:

```bash
uvicorn app.main:app --reload
```

## Endpoints iniciales

- `GET /api/v1/health`
- `GET /api/v1/wallet/me`
- `POST /api/v1/payments/simulate-retained`
- `POST /api/v1/wallet/withdrawals`
- `POST /api/v1/trips/vehicle`
- `POST /api/v1/trips/public-transport`
- `POST /api/v1/safety/accompaniment/start`
- `POST /api/v1/safety/accompaniment/{accompaniment_id}/safe`
- `POST /api/v1/safety/sos/trigger`
- `POST /api/v1/participation/join`
- `POST /api/v1/participation/trips/{trip_id}/participants/{participant_id}/decision`
- `POST /api/v1/participation/trips/{trip_id}/status`
- `POST /api/v1/participation/ratings`
- `POST /api/v1/routes/reports`
- `POST /api/v1/routes/reports/{report_id}/vote`
- `POST /api/v1/profile/emergency-contacts`
- `PUT /api/v1/profile/emergency-contacts/{contact_id}`
- `DELETE /api/v1/profile/emergency-contacts/{contact_id}`
- `WS /api/v1/chat/ws/trips/{trip_id}?token=<jwt>`

## Autenticación

La API valida JWT reales de Supabase (`Authorization: Bearer <token>`) con JWKS.
El usuario autenticado se cruza con `public.users` para obtener `campus_id` e `is_admin`.

## Worker

Se inicia un scheduler APScheduler en el lifespan de FastAPI para revisar expiraciones de sesiones de Acompáñame y detonar `alerta_detonada` automáticamente.

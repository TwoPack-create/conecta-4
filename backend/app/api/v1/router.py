from fastapi import APIRouter

from app.api.v1.endpoints import chat, health, participation, payments, profile, routes, safety, trips, wallet

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(wallet.router)
api_router.include_router(payments.router)
api_router.include_router(trips.router)
api_router.include_router(safety.router)
api_router.include_router(participation.router)
api_router.include_router(routes.router)
api_router.include_router(profile.router)
api_router.include_router(chat.router)

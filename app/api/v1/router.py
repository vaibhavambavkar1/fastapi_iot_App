from fastapi import APIRouter

from app.api.v1.endpoints import devices, health, telemetry

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    devices.router,
    prefix="/devices",
    tags=["devices"],
)

api_router.include_router(
    telemetry.router,
    tags=["telemetry"],
)

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_device_service
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter()


@router.post(
    "",
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_device(
    payload: DeviceCreate,
    service: DeviceService = Depends(get_device_service),
):
    return service.create_device(payload)


@router.get(
    "",
    response_model=list[DeviceRead],
)
def list_devices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    service: DeviceService = Depends(get_device_service),
):
    return service.list_devices(skip=skip, limit=limit)


@router.get(
    "/{device_id}",
    response_model=DeviceRead,
)
def get_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
):
    return service.get_device(device_id)


@router.patch(
    "/{device_id}",
    response_model=DeviceRead,
)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    service: DeviceService = Depends(get_device_service),
):
    return service.update_device(device_id, payload)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
):
    service.delete_device(device_id)

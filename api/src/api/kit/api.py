from typing import Annotated
from fastapi import APIRouter, Body

from .schemes import (
    KitCreateDto,
    KitDeleteDto,
    KitFiltersDep,
    KitPageResponse,
    KitResponse,
    KitUpdateDto,
)
from .service import KitServiceDep
from src.core import PageRequestDep

router = APIRouter(prefix="/kit", tags=["kit"])


@router.get("/", response_model=KitPageResponse)
async def list_kits(
    service: KitServiceDep,
    page: PageRequestDep,
    filters: KitFiltersDep,
):
    return await service.list(page, filters)


@router.post("/", response_model=KitResponse, status_code=201)
async def create_kit(
    payload: Annotated[KitCreateDto, Body(embed=False)],
    service: KitServiceDep,
):
    result = await service.create(payload)
    return KitResponse.model_validate(result, from_attributes=True)


@router.patch("/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: int,
    data: KitUpdateDto,
    service: KitServiceDep,
):
    return await service.update(kit_id, data)


@router.delete("/{kit_id}", status_code=204)
async def delete_kit(
    kit_id: int,
    service: KitServiceDep,
):
    await service.delete(KitDeleteDto(id=kit_id))
    return None

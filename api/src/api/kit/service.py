from typing import Annotated
from fastapi import Depends, HTTPException
from .repository import KitRepository, KitRepositoryDep
from .schemes import (
    KitCreateDto,
    KitDeleteDto,
    KitFilters,
    KitResponse,
    KitUpdateDto,
    KitPageResponse,
)
from core import PageRequest


class KitService:
    def __init__(self, repository: KitRepository) -> None:
        self._repository = repository

    async def create(self, kit: KitCreateDto):
        return await self._repository.create(kit.model_dump())

    async def update(self, kit_id: int, data: KitUpdateDto) -> KitResponse:
        result = await self._repository.update(kit_id, data.model_dump())
        if result is None:
            raise HTTPException(400, "Kit not found")
        return KitResponse.model_validate(result, from_attributes=True)

    async def delete(self, kit: KitDeleteDto) -> None:
        result = await self._repository.delete(kit.id)
        if not result:
            raise HTTPException(400, "Kit not found")
        return

    async def list(
        self, page_request: PageRequest, filters: KitFilters
    ) -> KitPageResponse:
        kits = await self._repository.list(
            filters=filters.model_dump(exclude_unset=True),
            offset=page_request.offset,
            limit=page_request.page_size,
        )
        return KitPageResponse(
            items=[
                KitResponse.model_validate(kit, from_attributes=True) for kit in kits
            ],
            **page_request.model_dump(),
        )


def get_kit_service(repository: KitRepositoryDep):
    return KitService(repository)


KitServiceDep = Annotated[KitService, Depends(get_kit_service)]

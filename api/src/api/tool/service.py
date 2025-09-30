from typing import Annotated
from fastapi import Depends, HTTPException
from .repository import ToolRepository, ToolRepositoryDep
from .schemes import (
    ToolCreateDto,
    ToolDeleteDto,
    ToolFilters,
    ToolResponse,
    ToolUpdateDto,
    ToolPageResponse,
)
from src.core import PageRequest


class ToolService:
    def __init__(self, repository: ToolRepository) -> None:
        self._repository = repository

    async def create(self, tool: ToolCreateDto):
        return await self._repository.create(tool.model_dump())

    async def update(self, tool_id: int, data: ToolUpdateDto) -> ToolResponse:
        result = await self._repository.update(tool_id, data.model_dump())
        if result is None:
            raise HTTPException(400, "Tool not found")
        return ToolResponse.model_validate(result, from_attributes=True)

    async def delete(self, tool: ToolDeleteDto) -> None:
        result = await self._repository.delete(tool.id)
        if not result:
            raise HTTPException(400, "Tool not found")
        return

    async def list(
        self, page_request: PageRequest, filters: ToolFilters
    ) -> ToolPageResponse:
        tools = await self._repository.list(
            filters=filters.model_dump(exclude_unset=True),
            offset=page_request.offset,
            limit=page_request.page_size,
        )
        return ToolPageResponse(
            items=[
                ToolResponse.model_validate(tool, from_attributes=True)
                for tool in tools[0]
            ],
            page_number=page_request.page_number,
            page_size=page_request.page_size,
            total=tools[1],
        )


def get_tool_service(repository: ToolRepositoryDep):
    return ToolService(repository)


ToolServiceDep = Annotated[ToolService, Depends(get_tool_service)]

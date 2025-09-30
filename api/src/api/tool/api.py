from typing import Annotated
from fastapi import APIRouter, Body
from .schemes import (
    ToolCreateDto,
    ToolDeleteDto,
    ToolFiltersDep,
    ToolPageResponse,
    ToolResponse,
    ToolUpdateDto,
)
from .service import ToolServiceDep
from src.core import PageRequestDep

router = APIRouter(prefix="/tool", tags=["tool"])


@router.get("/", response_model=ToolPageResponse)
async def list_tools(
    service: ToolServiceDep,
    page: PageRequestDep,
    filters: ToolFiltersDep,
):
    return await service.list(page, filters)


@router.post("/", response_model=ToolResponse, status_code=201)
async def create_tool(
    payload: Annotated[ToolCreateDto, Body(embed=False)],
    service: ToolServiceDep,
):
    result = await service.create(payload)
    return ToolResponse.model_validate(result, from_attributes=True)


@router.patch("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: int,
    data: ToolUpdateDto,
    service: ToolServiceDep,
):
    return await service.update(tool_id, data)


@router.delete("/{tool_id}", status_code=204)
async def delete_tool(
    tool_id: int,
    service: ToolServiceDep,
):
    await service.delete(ToolDeleteDto(id=tool_id))
    return None

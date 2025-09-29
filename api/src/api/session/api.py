from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Form
import json

from api.analyze.service import AnalyzeServiceDep

from .schemes import (
    SessionCreateDto,
    SessionFilters,
    SessionPageResponse,
    SessionDetailsResponse,
)
from .service import SessionServiceDep
from src.core.schemes import ID_TYPE, PageRequest

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/", response_model=SessionPageResponse)
async def list_sessions(
    service: SessionServiceDep,
    page: PageRequest,
    filters: SessionFilters = SessionFilters(),
) -> SessionPageResponse:
    return await service.list(page, filters)


@router.get("/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: ID_TYPE,
    service: SessionServiceDep,
) -> SessionDetailsResponse:
    return await service.session_details_info(session_id)


@router.post("/", response_model=SessionDetailsResponse)
async def initialize_session(
    service: SessionServiceDep,
    analyze_service: AnalyzeServiceDep,
    session_data: SessionCreateDto,
    image: Annotated[UploadFile, File()],
):
    image_data = await image.read()
    tools_recognized = analyze_service.analyze(image_data)

    return await service.initialize_session(
        session_data=session_data,
        image_recognized=image_data,
        tools_recognized=tools_recognized["items"],  # type: ignore
    )


@router.post("/{session_id}/open", response_model=SessionDetailsResponse)
async def open_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
):
    """Open a session for tool usage."""
    return await service.session_open(session_id)


@router.post("/{session_id}/preclose", response_model=SessionDetailsResponse)
async def preclose_session(
    session_id: ID_TYPE,
    analyze_service: AnalyzeServiceDep,
    service: SessionServiceDep,
    image: Annotated[UploadFile, File()],
):
    image_data = await image.read()
    tools_recognized = analyze_service.analyze(image_data)

    return await service.session_preclose(
        session_id=session_id,
        image_recognized=image_data,
        tools_recognized=tools_recognized["items"],  # type: ignore
    )


@router.post("/{session_id}/close", response_model=SessionDetailsResponse)
async def close_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
):
    return await service.session_close(session_id)

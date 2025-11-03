from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from application.session.dtos import (
    SessionCreateDto,
    SessionDetailsResponse,
    SessionFiltersDep,
    SessionPageResponse,
    SessionResponse,
)
from application.session.service import SessionServiceDep
from application.shared.dtos import Page
from application.shared import PageRequestDep
from domain.session.entities.session import Session
from domain.shared import ID_TYPE

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/", response_model=Page[SessionResponse])
async def list_sessions(
    service: SessionServiceDep,
    page: PageRequestDep,
    filters: SessionFiltersDep,
) -> Page[Session]:
    return await service.get_page(filters, page)


@router.get("/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: ID_TYPE,
    service: SessionServiceDep,
) -> Session:
    return await service.get_one_or_raise(session_id)


# Using Forms is the only way to set up multipart data
@router.post("/", response_model=SessionDetailsResponse)
async def initialize_session(
    service: SessionServiceDep,
    reciever_id: Annotated[int, Form()],
    location_id: Annotated[int, Form()],
    kit_id: Annotated[int, Form()],
    image: Annotated[UploadFile, File()],
) -> Session:
    session_data = SessionCreateDto(
        reciever_id=reciever_id,
        location_id=location_id,
        kit_id=kit_id,
    )
    image_data = await image.read()
    session = await service.initialize_session(session_data, image_data)
    return session


@router.post("/{session_id}/open", response_model=SessionDetailsResponse)
async def open_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
) -> Session:
    return await service.session_open(session_id)


@router.post("/{session_id}/preclose", response_model=SessionDetailsResponse)
async def preclose_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
    image: Annotated[UploadFile, File()],
) -> Session:
    image_data = await image.read()
    return await service.session_preclose(
        session_id=session_id,
        image=image_data,
    )


@router.post("/{session_id}/close", response_model=SessionDetailsResponse)
async def close_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
) -> Session:
    return await service.session_close(session_id)

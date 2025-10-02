from typing import Annotated
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.api.recognize import RecognizeServiceDep

from .schemes import (
    SessionCreateDto,
    SessionFiltersDep,
    SessionPageResponse,
    SessionDetailsResponse,
)
from .service import SessionServiceDep
from src.core import ID_TYPE
from src.core import PageRequestDep

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/", response_model=SessionPageResponse)
async def list_sessions(
    service: SessionServiceDep,
    page: PageRequestDep,
    filters: SessionFiltersDep,
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
    recognize_service: RecognizeServiceDep,
    reciever_id: Annotated[int, Form()],
    location_id: Annotated[int, Form()],
    kit_id: Annotated[int, Form()],
    image: Annotated[UploadFile, File()],
):
    session_data = SessionCreateDto(
        reciever_id=reciever_id,
        location_id=location_id,
        kit_id=kit_id,
    )
    image_data = await image.read()
    tools_recognized = (await recognize_service.recognize([image_data]))[0]
    if not tools_recognized.success:
        raise HTTPException(
            status_code=500,
            detail="Recognition service error, try again in a few minutes",
        )
    image_drawn_boxes = recognize_service.draw_boxes(
        image_data, tools_recognized.detections
    )
    return await service.initialize_session(
        session_data=session_data,
        image_recognized=image_drawn_boxes,
        detections=tools_recognized.detections,
    )


@router.post("/{session_id}/open", response_model=SessionDetailsResponse)
async def open_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
):
    return await service.session_open(session_id)


@router.post("/{session_id}/preclose", response_model=SessionDetailsResponse)
async def preclose_session(
    session_id: ID_TYPE,
    recognize_service: RecognizeServiceDep,
    service: SessionServiceDep,
    image: Annotated[UploadFile, File()],
):
    image_data = await image.read()
    tools_recognized = (await recognize_service.recognize([image_data]))[0]
    if not tools_recognized.success:
        raise HTTPException(
            status_code=500,
            detail="Recognition service error, try again in a few minutes",
        )

    image_drawn_boxes = recognize_service.draw_boxes(
        image_data, tools_recognized.detections
    )

    return await service.session_preclose(
        session_id=session_id,
        image_recognized=image_drawn_boxes,
        detections=tools_recognized.detections,
    )


@router.post("/{session_id}/close", response_model=SessionDetailsResponse)
async def close_session(
    session_id: ID_TYPE,
    service: SessionServiceDep,
):
    return await service.session_close(session_id)

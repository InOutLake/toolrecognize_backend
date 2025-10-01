from collections import Counter
from typing import Annotated
import uuid
from fastapi import Depends, HTTPException
from src.api.recognize import Detection
from src.storage import AsyncS3Repository, AsyncS3RepositoryDep
from src.database import Session, SessionStatus, SessionTool
from src.api.session_tool.repository import (
    SessionToolRepository,
    SessionToolRepositoryDep,
)
from src.core import ID_TYPE, SETTINGS, PageRequest
from src.api.session.repository import SessionRepository, SessionRepositoryDep
from src.api.session.schemes import (
    SessionCreateDto,
    SessionDetailsResponse,
    SessionFilters,
    SessionResponse,
    SessionToolDto,
    SessionUpdateDto,
    SessionPageResponse,
)


class SessionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(400, "Session not found")


class SessionService:
    def __init__(
        self,
        session_repository: SessionRepository,
        s3_repository: AsyncS3Repository,
        session_tool_repository: SessionToolRepository,
    ) -> None:
        self._session_repository = session_repository
        self._s3_repository = s3_repository
        self._session_tool_repository = session_tool_repository

    async def create(self, session: SessionCreateDto) -> SessionResponse:
        new_session = await self._session_repository.create(session.model_dump())
        return SessionResponse.model_validate(new_session, from_attributes=True)

    async def _aggregate_session_tools_info(
        self, session_id: ID_TYPE
    ) -> list[SessionToolDto]:
        all_tools = await self._session_repository.full_tools_info(session_id)
        return [
            SessionToolDto.model_validate(row, from_attributes=True)
            for row in all_tools
        ]

    async def _get_session(self, session_id: ID_TYPE) -> Session:
        session = await self._session_repository.get_one(filters={"id": session_id})
        if session is None:
            raise SessionNotFoundException()

        return session

    async def session_details_info(self, session_id: ID_TYPE) -> SessionDetailsResponse:
        session = await self._get_session(session_id)
        session_tools_info = await self._aggregate_session_tools_info(session_id)
        result = SessionDetailsResponse.model_validate(session, from_attributes=True)
        if session.given_image_key is not None:
            result.given_image_url = await self._s3_repository.generate_presigned_url(
                key=session.given_image_key
            )
        if session.returned_image_key is not None:
            result.returned_image_url = (
                await self._s3_repository.generate_presigned_url(
                    key=session.returned_image_key
                )
            )
        result.tools = session_tools_info
        return result

    def _map_detetctions_to_tools(
        self, detections: list[Detection]
    ) -> dict[ID_TYPE, int]:
        tools_counted = dict(Counter(detection.class_id for detection in detections))
        return {
            SETTINGS.tools_mapping[class_id]: quantity
            for class_id, quantity in tools_counted.items()
        }

    async def initialize_session(
        self,
        session_data: SessionCreateDto,
        image_recognized: bytes,
        detections: list[Detection],
    ) -> SessionDetailsResponse:
        tools_recognized = self._map_detetctions_to_tools(detections)
        data = session_data.model_dump()
        data["status"] = SessionStatus.open_waiting_for_aproval.value
        session = await self._session_repository.create(data)
        session_tools = [
            SessionTool(
                tool_id=id,
                session_id=session.id,
                quantity_given=quantity,
                quantity_returned=0,
            )
            for id, quantity in tools_recognized.items()
        ]
        await self._session_tool_repository.create_many(session_tools)
        image_url = await self._s3_repository.upload_file(
            key=str(uuid.uuid4()), data=image_recognized
        )
        session = await self._session_repository.update(
            session.id,
            {
                "given_image_key": image_url,
            },
        )
        return await self.session_details_info(session.id)  # type: ignore

    async def session_open(self, session_id: ID_TYPE) -> SessionDetailsResponse:
        await self._session_repository.open_session(session_id)
        return await self.session_details_info(session_id)

    async def session_preclose(
        self,
        session_id: ID_TYPE,
        image_recognized: bytes,
        detections: list[Detection],
    ) -> SessionDetailsResponse:
        session = await self._get_session(session_id)
        tools_recognized = self._map_detetctions_to_tools(detections)
        updates = []
        for tool in session.session_tools:
            if tool.tool_id in tools_recognized.keys():
                updates.append(
                    (tool.id, {"quantity_returned": tools_recognized[tool.tool_id]})  # type: ignore
                )

        if updates:
            await self._session_tool_repository.update_many(updates)

        image_url = await self._s3_repository.upload_file(
            key=str(uuid.uuid4()), data=image_recognized
        )
        await self._session_repository.update(
            session.id,
            {
                "returned_image_key": image_url,
                "status": SessionStatus.close_waiting_for_aproval,
            },
        )
        return await self.session_details_info(session_id)

    async def session_close(self, session_id: ID_TYPE) -> SessionDetailsResponse:
        await self._session_repository.close_session(session_id)
        return await self.session_details_info(session_id)

    async def update(self, session: SessionUpdateDto) -> SessionResponse:
        result = await self._session_repository.update(session.id, session.model_dump())
        if result is None:
            raise SessionNotFoundException()
        return SessionResponse.model_validate(result, from_attributes=True)

    async def delete(self, session_id: ID_TYPE) -> None:
        result = await self._session_repository.delete(session_id)
        if result is None:
            raise HTTPException(400, "Session not found")
        return

    async def list(
        self, page_request: PageRequest, filters: SessionFilters
    ) -> SessionPageResponse:
        sessions = await self._session_repository.list(
            filters=filters.model_dump(exclude_unset=True),
            offset=page_request.offset,
            limit=page_request.page_size,
        )
        return SessionPageResponse(
            items=[
                SessionResponse.model_validate(session, from_attributes=True)
                for session in sessions[0]
            ]
            if sessions[0]
            else [],
            page_number=page_request.page_number,
            page_size=page_request.page_size,
            total=sessions[1],
        )


def get_session_service(
    session_repository: SessionRepositoryDep,
    s3_repository: AsyncS3RepositoryDep,
    session_tool_repository: SessionToolRepositoryDep,
):
    return SessionService(session_repository, s3_repository, session_tool_repository)


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]

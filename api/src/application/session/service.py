import uuid
from typing import Annotated

from fastapi import Depends, HTTPException

from application import CRUDService, CRUDServiceProtocol
from application.recognition import (
    DetectionToolMapper,
    DetectionToolMapperDep,
    RecognitionServiceDep,
    RecognitionServiceProtocol,
)
from domain.session import Session
from domain.shared import ID_TYPE
from infrastructure.repositories.s3 import S3RepositoryDep, S3RepositoryProtocol
from infrastructure.repositories.session import (
    SessionRepositoryDep,
    SessionRepositoryProtocol,
)

from .dtos import (
    SessionCreateDto,
    SessionFilters,
    SessionUpdateDto,
)


class SessionServiceProtocol(
    CRUDServiceProtocol[Session, SessionCreateDto, SessionUpdateDto, SessionFilters]
):
    def __init__(
        self,
        session_repository: SessionRepositoryProtocol,
        s3_repository: S3RepositoryProtocol,
        recognition_service: RecognitionServiceProtocol,
        detections_mapper: ...,
    ) -> None: ...

    async def initialize_session(
        self,
        session_data: SessionCreateDto,
        image: bytes,
    ) -> Session: ...
    async def session_open(self, session_id: ID_TYPE) -> Session: ...
    async def session_preclse(
        self,
        session_id: ID_TYPE,
        image: bytes,
    ) -> Session: ...
    async def session_close(self, session_id: ID_TYPE) -> Session: ...


class SessionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(400, "Session not found")


class SessionService(
    SessionServiceProtocol,
    CRUDService[Session, SessionCreateDto, SessionUpdateDto, SessionFilters],
):
    def __init__(
        self,
        session_repository: SessionRepositoryProtocol,
        s3_repository: S3RepositoryProtocol,
        recognition_service: RecognitionServiceProtocol,
        detections_mapper: DetectionToolMapper,
    ) -> None:
        self._session_repository = session_repository
        self._s3_repository = s3_repository
        self._recognition_service = recognition_service
        self._detections_mapper = detections_mapper

    async def get_one_or_raise(self, session_id: ID_TYPE):
        entity = await self._session_repository.get_one(filters={"id": session_id})
        if not entity:
            raise SessionNotFoundException()
        return Session.model_validate(entity, from_attributes=True)

    async def initialize_session(
        self,
        session_data: SessionCreateDto,
        image: bytes,
    ) -> Session:
        session = Session.create(**session_data.model_dump())
        detections = (await self._recognition_service.recognize_tools([image]))[0]
        tools_recognized = self._detections_mapper.map(detections)
        key = await self._s3_repository.upload_file(
            key=str(uuid.uuid4()),
            data=image,
        )
        session.preopen(key, tools_recognized)
        session = (await self._session_repository.save([session]))[0]
        return session

    async def session_open(self, session_id: ID_TYPE) -> Session:
        session = await self.get_one_or_raise(session_id)
        session.open()
        session = (await self._session_repository.save([session]))[0]
        return session

    async def session_preclose(
        self,
        session_id,
        image: bytes,
    ) -> Session:
        session = await self.get_one_or_raise(session_id)
        detections = (await self._recognition_service.recognize_tools([image]))[0]
        tools_recognized = self._detections_mapper.map(detections)
        key = await self._s3_repository.upload_file(
            key=str(uuid.uuid4()),
            data=image,
        )
        session.preclose(key, tools_recognized)
        session = (await self._session_repository.save([session]))[0]
        return session

    async def session_close(self, session_id) -> Session:
        session = await self.get_one_or_raise(session_id)
        session.close()
        session = (await self._session_repository.save([session]))[0]
        return session


def get_session_service(
    session_repository: SessionRepositoryDep,
    s3_repository: S3RepositoryDep,
    recognition_service: RecognitionServiceDep,
    detections_mapper: DetectionToolMapperDep,
) -> SessionServiceProtocol:
    return SessionService(
        session_repository,
        s3_repository,
        recognition_service,
        detections_mapper,
    )


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]

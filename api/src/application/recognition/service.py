from typing import Annotated, Protocol

from fastapi import Depends
from domain.recognition import Detection
from infrastructure.repositories.recognition import (
    RecognitionRepositoryProtocol,
    RecognitionRepositoryDep,
)


class RecognitionServiceProtocol(Protocol):
    def __init__(self, recognition_repository: RecognitionRepositoryProtocol): ...
    async def recognize_tools(self, images: list[bytes]) -> list[list[Detection]]: ...


class RecognitionService(RecognitionServiceProtocol):
    def __init__(self, recognition_repository: RecognitionRepositoryProtocol):
        self._recognition_repository = recognition_repository

    async def recognize_tools(self, images: list[bytes]) -> list[list[Detection]]:
        return await self._recognition_repository.recognize(images)


def get_recognition_service(
    recognition_repository: RecognitionRepositoryDep,
) -> RecognitionServiceProtocol:
    return RecognitionService(recognition_repository)


RecognitionServiceDep = Annotated[
    RecognitionServiceProtocol,
    Depends(get_recognition_service),
]

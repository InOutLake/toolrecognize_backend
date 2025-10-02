from typing import Annotated, Protocol
from fastapi import Depends


from .repository import RecognizeRepositoryDep, RecognizeRepositoryProtocol
from .schemes import DetectResponse, Detection, DetectionBBox


class RecognizeServiceMock:
    def recognize(self, image: bytes) -> DetectResponse:
        detections = [
            Detection(
                class_id=1,
                class_name="brace",
                confidence=0.99,
                bbox=DetectionBBox(x1=10, y1=20, x2=110, y2=120),
            ),
            Detection(
                class_id=2,
                class_name="screwdriver_cross",
                confidence=0.95,
                bbox=DetectionBBox(x1=30, y1=40, x2=130, y2=140),
            ),
        ]
        return DetectResponse(
            detections=detections,
            total_detections=len(detections),
        )


class RecognizeService:
    def __init__(self, repository: RecognizeRepositoryProtocol):
        self._repository = repository

    async def recognize(self, images: list[bytes]) -> list[DetectResponse]:
        return await self._repository.recognize(images)


def get_recognize_service(repository: RecognizeRepositoryDep):
    return RecognizeService(repository)


RecognizeServiceDep = Annotated[RecognizeService, Depends(get_recognize_service)]

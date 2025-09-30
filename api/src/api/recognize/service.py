from typing import Annotated
from fastapi import Depends


import httpx
from src.core import SETTINGS
from .schemes import DetectResponse, Detection, DetectionBBox, ImageInfo


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
        image_info = ImageInfo(width=640, height=480, mode="RGB")
        return DetectResponse(
            detections=detections,
            total_detections=len(detections),
            image_info=image_info,
        )


class RecognizeService:
    def __init__(self):
        self.api_url = SETTINGS.recognize_api_url
        self.api_key = SETTINGS.recognize_api_key

    async def analyze(self, image: bytes) -> DetectResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": ("image.jpg", image, "image/jpeg")}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=headers, files=files)
            response.raise_for_status()

        return DetectResponse(**response.json())


class ReService:
    def __init__(self):
        self.api_url = SETTINGS.recognize_api_url
        self.api_key = SETTINGS.recognize_api_key

    async def analyze(self, image: bytes) -> DetectResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": ("image.jpg", image, "image/jpeg")}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=headers, files=files)
            response.raise_for_status()

        return DetectResponse(**response.json())


def get_recognize_service():
    return RecognizeServiceMock()


RecognizeServiceDep = Annotated[RecognizeServiceMock, Depends(get_recognize_service)]

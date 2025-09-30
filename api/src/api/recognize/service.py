from typing import Annotated
from fastapi import Depends


import httpx
from src.core import SETTINGS
from .schemes import DetectResponse


class AnalyzeService:
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


def get_analyze_service():
    return AnalyzeService()


AnalyzeServiceDep = Annotated[AnalyzeService, Depends(get_analyze_service)]

from typing import Annotated, Any
from fastapi import Depends


import requests
from src.core import SETTINGS
from .schemes import DetectResponse


class AnalyzeService:
    def __init__(self):
        self.api_url = SETTINGS.analyze_api_url
        self.api_key = SETTINGS.analyze_api_key

    def analyze(self, image: bytes) -> DetectResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": ("image.jpg", image, "image/jpeg")}
        response = requests.post(self.api_url, headers=headers, files=files)
        response.raise_for_status()

        return DetectResponse(**response.json())


def get_analyze_service():
    return AnalyzeService()


AnalyzeServiceDep = Annotated[AnalyzeService, Depends(get_analyze_service)]

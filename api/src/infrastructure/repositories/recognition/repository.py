import asyncio
import base64
from typing import Annotated, Protocol

import httpx
from fastapi import Depends
from faststream.rabbit import RabbitBroker

from core import SETTINGS
from domain.recognition import Detection
from infrastructure.repositories.broker import BrokerDep

from .dtos import DetectRequest, DetectResponse


class RecognitionRepositoryProtocol(Protocol):
    async def recognize(self, images: list[bytes]) -> list[list[Detection]]: ...


class RecognitionRepositoryAmqp(RecognitionRepositoryProtocol):
    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker

    async def recognize(self, images: list[bytes]) -> list[list[Detection]]:
        tasks = [
            self._broker.publish(
                DetectRequest(image_bytes=base64.b64encode(image).decode("utf-8")),
                queue="detect_queue",
                rpc=True,
            )
            for image in images
        ]
        responses = await asyncio.gather(*tasks)
        responses = [DetectResponse.model_validate(result) for result in responses]
        return [response.detections for response in responses]


class RecognitionRepositoryHttp(RecognitionRepositoryProtocol):
    def __init__(self) -> None:
        self.api_url = SETTINGS.recognize_api_url
        self.api_key = SETTINGS.recognize_api_key

    async def recognize(self, images: list[bytes]) -> list[list[Detection]]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        results = []
        async with httpx.AsyncClient() as client:
            for image in images:
                files = {"file": ("image.jpg", image, "image/jpeg")}
                response = await client.post(self.api_url, headers=headers, files=files)
                response.raise_for_status()
                results.append(DetectResponse(**response.json()).detections)
        return results


def get_recognize_repository(broker: BrokerDep) -> RecognitionRepositoryProtocol:
    if SETTINGS.recognize_app_mode == "amqp":
        return RecognitionRepositoryAmqp(broker)
    else:
        return RecognitionRepositoryHttp()


RecognitionRepositoryDep = Annotated[
    RecognitionRepositoryProtocol, Depends(get_recognize_repository)
]

import base64
from typing import Annotated, Protocol
from fastapi import Depends
from faststream.rabbit import RabbitBroker
import httpx
from .schemes import DetectResponse, DetectRequest
from src.core import SETTINGS, BrokerDep
import asyncio


class RecognizeRepositoryProtocol(Protocol):
    async def recognize(self, images: list[bytes]) -> list[DetectResponse]: ...


class RecognizeRepositoryAmqp(RecognizeRepositoryProtocol):
    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker

    async def recognize(self, images: list[bytes]) -> list[DetectResponse]:
        tasks = [
            self._broker.publish(
                DetectRequest(image_bytes=base64.b64encode(image).decode("utf-8")),
                queue="detect_queue",
                rpc=True,
            )
            for image in images
        ]
        results = await asyncio.gather(*tasks)
        return [DetectResponse.model_validate(result) for result in results]


class RecognizeRepositoryHttp(RecognizeRepositoryProtocol):
    def __init__(self) -> None:
        self.api_url = SETTINGS.recognize_api_url
        self.api_key = SETTINGS.recognize_api_key

    async def recognize(self, images: list[bytes]) -> list[DetectResponse]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        results = []
        async with httpx.AsyncClient() as client:
            for image in images:
                files = {"file": ("image.jpg", image, "image/jpeg")}
                response = await client.post(self.api_url, headers=headers, files=files)
                response.raise_for_status()
                results.append(DetectResponse(**response.json()))
        return results


def get_recognize_repository(broker: BrokerDep) -> RecognizeRepositoryProtocol:
    if SETTINGS.recognize_app_mode == "amqp":
        return RecognizeRepositoryAmqp(broker)
    else:
        return RecognizeRepositoryHttp()


RecognizeRepositoryDep = Annotated[
    RecognizeRepositoryProtocol, Depends(get_recognize_repository)
]

from typing import Annotated
from click import File
from fastapi import APIRouter, UploadFile

from .schemes import DetectResponse
from .service import RecognizeServiceDep

router = APIRouter(prefix="/recognize", tags=["recognize"])


@router.post("/", response_model=list[DetectResponse])
async def recognize(
    recognize_service: RecognizeServiceDep,
    image: list[UploadFile],
) -> list[DetectResponse]:
    return [await recognize_service.recognize(await img.read()) for img in image]

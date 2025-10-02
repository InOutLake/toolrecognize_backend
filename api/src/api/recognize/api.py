from fastapi import APIRouter, UploadFile

from .schemes import DetectResponseWithImage
from .service import RecognizeServiceDep
import base64

router = APIRouter(prefix="/recognize", tags=["recognize"])


@router.post("/", response_model=list[DetectResponseWithImage])
async def recognize(
    recognize_service: RecognizeServiceDep,
    images: list[UploadFile],
) -> list[DetectResponseWithImage]:
    images_bytes = [await img.read() for img in images]
    detections = await recognize_service.recognize(images_bytes)
    images_with_boxes = [
        recognize_service.draw_boxes(image, detections[i].detections)
        for i, image in enumerate(images_bytes)
    ]
    return [
        DetectResponseWithImage(
            **detections[i].model_dump(),
            image=base64.b64encode(image).decode("utf-8"),
        )
        for i, image in enumerate(images_with_boxes)
    ]

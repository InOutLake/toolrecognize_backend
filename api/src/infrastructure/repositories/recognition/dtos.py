from pydantic import BaseModel
from src.domain.recognition import Detection


class DetectResponse(BaseModel):
    success: bool = True
    detections: list[Detection]
    total_detections: int


class DetectRequest(BaseModel):
    image_bytes: str


class DetectResponseWithImage(DetectResponse):
    image: str

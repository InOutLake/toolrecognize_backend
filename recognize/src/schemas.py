from pydantic import BaseModel


class DetectionBBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: DetectionBBox


class DetectResponse(BaseModel):
    success: bool = True
    detections: list[Detection]
    total_detections: int


class DetectRequest(BaseModel):
    image_bytes: str

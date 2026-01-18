from pydantic import BaseModel
 domain.shared import ID_TYPE


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

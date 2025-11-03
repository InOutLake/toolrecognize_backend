from typing import Any
from pydantic import BaseModel

from src.domain.shared import Domain


class DetectionBBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(Domain):
    class_id: Any
    class_name: str
    confidence: float
    bbox: DetectionBBox

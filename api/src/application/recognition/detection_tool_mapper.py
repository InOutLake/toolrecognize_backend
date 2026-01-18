from typing import Annotated, Any

from fastapi import Depends
from core import SETTINGS
from domain.shared import ID_TYPE
from domain.session import ToolQuantity
from collections import Counter
from domain.recognition import Detection


class DetectionToolMapper:
    def __init__(self, tool_map: dict[Any, ID_TYPE]):
        self.tool_map = tool_map

    def map(self, detections: list[Detection]) -> list[ToolQuantity]:
        tools_counted = Counter(detection.class_id for detection in detections)
        return [
            ToolQuantity(
                tool_id=self.tool_map[tool_id],
                quantity=quantity,
            )
            for tool_id, quantity in tools_counted.items()
        ]


def get_detection_tool_mapper() -> DetectionToolMapper:
    return DetectionToolMapper(SETTINGS.tools_mapping)


DetectionToolMapperDep = Annotated[
    DetectionToolMapper, Depends(get_detection_tool_mapper)
]

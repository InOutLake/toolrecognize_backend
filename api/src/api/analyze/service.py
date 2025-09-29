from typing import Annotated, Any
from fastapi import Depends


class AnalyzeServiceMock:
    def analyze(self, image: bytes) -> dict[str, Any]:
        return {
            "analyzed_image": b"some image bytes",
            "items": {
                "brace": 1,
                "screwdriver_cross": 1,
                "screwdriver_shift_cross": 1,
                "shernitsa": 1,
            },
        }


def get_analyze_service():
    return AnalyzeServiceMock()


AnalyzeServiceDep = Annotated[AnalyzeServiceMock, Depends(get_analyze_service)]

from .service import RecognizeServiceDep
from .schemes import Detection
from .api import router as recognize_router

__all__ = ["RecognizeServiceDep", "Detection", "recognize_router"]

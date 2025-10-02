from io import BytesIO
from typing import Annotated
from fastapi import Depends


from .repository import RecognizeRepositoryDep, RecognizeRepositoryProtocol
from .schemes import DetectResponse, Detection, DetectionBBox
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class RecognizeServiceMock:
    def recognize(self, image: bytes) -> DetectResponse:
        detections = [
            Detection(
                class_id=1,
                class_name="brace",
                confidence=0.99,
                bbox=DetectionBBox(x1=10, y1=20, x2=110, y2=120),
            ),
            Detection(
                class_id=2,
                class_name="screwdriver_cross",
                confidence=0.95,
                bbox=DetectionBBox(x1=30, y1=40, x2=130, y2=140),
            ),
        ]
        return DetectResponse(
            detections=detections,
            total_detections=len(detections),
        )


class RecognizeService:
    def __init__(self, repository: RecognizeRepositoryProtocol):
        self._repository = repository

    async def recognize(self, images: list[bytes]) -> list[DetectResponse]:
        return await self._repository.recognize(images)

    def draw_boxes(self, image: bytes, detections: list[Detection]) -> bytes:
        img = Image.open(BytesIO(image)).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", size=14)
        except IOError:
            font = ImageFont.load_default()

        # Draw each detection
        for det in detections:
            box = det.bbox
            x1, y1, x2, y2 = box.x1, box.y1, box.x2, box.y2
            label = f"{det.class_id}: {det.class_name} {det.confidence:.2f}"

            # Box
            draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)

            # Label
            bbox = draw.textbbox((x1, y1), label, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.rectangle([(x1, y1 - text_h), (x1 + text_w, y1)], fill="red")
            draw.text((x1, y1 - text_h), label, fill="white", font=font)

            # Draw label text
            draw.text((x1, y1 - text_h), label, fill="white", font=font)

        output = BytesIO()
        img.save(output, format="JPEG")
        return output.getvalue()


def get_recognize_service(repository: RecognizeRepositoryDep):
    return RecognizeService(repository)


RecognizeServiceDep = Annotated[RecognizeService, Depends(get_recognize_service)]

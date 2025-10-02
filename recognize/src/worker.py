import io
import os
from PIL import Image
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from src.model import recognize
from .model import load_model

from .schemas import (
    DetectRequest,
    DetectResponse,
)
import base64

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
broker = RabbitBroker(RABBIT_URL)

detect_exchange = RabbitExchange("detect")
detect_queue = RabbitQueue("detect_queue", routing_key="detect")


@broker.subscriber(exchange=detect_exchange, queue=detect_queue)
async def detect_handler(msg: DetectRequest) -> DetectResponse:
    try:
        load_model()

        image_bytes = base64.b64decode(msg.image_bytes)
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")

        detections = recognize(image)

        return DetectResponse(
            detections=detections,
            total_detections=len(detections),
        )
    except Exception as e:
        return DetectResponse(
            success=False,
            detections=[],
            total_detections=0,
        )

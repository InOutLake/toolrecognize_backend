import os
from PIL import Image
from ultralytics import YOLO
from .schemas import Detection, DetectionBBox

THRESHOLD = float(os.getenv("RECOGNIZE_THRESHOLD", "0.7"))
model = None


def load_model():
    global model
    if model is None:
        model_path = "model.pt"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file {model_path} not found")
        model = YOLO(model_path)
        print(f"YOLO model loaded successfully from {model_path}")
    return model


def recognize(image: Image.Image) -> list[Detection]:
    if model is None:
        raise Exception("model is not loaded")
    results = model(image)

    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                if confidence >= THRESHOLD:
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names[class_id]
                    bbox = DetectionBBox(x1=x1, y1=y1, x2=x2, y2=y2)
                    detections.append(
                        Detection(
                            class_id=class_id,
                            class_name=class_name,
                            confidence=confidence,
                            bbox=bbox,
                        )
                    )

    return detections

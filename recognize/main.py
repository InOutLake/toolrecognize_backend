import os
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultralytics import YOLO
import torch
import uvicorn
from PIL import Image


API_KEY = os.getenv("RECOGNIZE_API_KEY", "your_api_key_here")


def api_key_dependency(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    key = auth.removeprefix("Bearer ").strip()
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


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


class ImageInfo(BaseModel):
    width: int
    height: int
    mode: str


class DetectResponse(BaseModel):
    success: bool = True
    detections: list[Detection]
    total_detections: int
    image_info: ImageInfo


model = None
THRESHOLD = float(os.getenv("RECOGNIZE_THRESHOLD", "0.7"))


def load_model():
    global model
    model_path = "model.pt"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    try:
        model = YOLO(model_path)
        print(f"YOLO model loaded successfully from {model_path}")
    except Exception as e:
        raise Exception(f"Failed to load YOLO model: {str(e)}")


@asynccontextmanager
async def lifespan(app):
    try:
        load_model()
    except Exception as e:
        print(f"Warning: Could not load model at startup: {e}")
        print("Model will be loaded on first request")
    yield


app = FastAPI(title="YOLO Detection API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "YOLO Detection API is running",
        "model_loaded": model is not None,
        "GPU available": torch.cuda.is_available(),
    }


@app.post("/detect")
async def detect_objects(
    file: UploadFile = File(...),
    # _: None = Depends(api_key_dependency),
):
    global model
    if model is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load model: {str(e)}"
            )

    # for type checker
    if model is None:
        raise HTTPException(status_code=500, detail="Failed to load model")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        if image is None:
            raise FileNotFoundError()

        if image.mode != "RGB":
            image = image.convert("RGB")

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

        response = DetectResponse(
            detections=detections,
            total_detections=len(detections),
            image_info=ImageInfo(
                width=image.width, height=image.height, mode=image.mode
            ),
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

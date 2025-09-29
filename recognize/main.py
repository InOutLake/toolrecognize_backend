import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image


# Use FastAPI lifespan event handler for model loading
from contextlib import asynccontextmanager

model = None


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


@app.get("/")
async def root():
    return {
        "message": "YOLO Detection API is running",
        "model_loaded": model is not None,
    }


@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    global model
    if model is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load model: {str(e)}"
            )

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
                    # Get box coordinates, confidence, and class
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names[class_id]

                    detection = {
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2),
                        },
                    }
                    detections.append(detection)

        return JSONResponse(
            content={
                "success": True,
                "detections": detections,
                "total_detections": len(detections),
                "image_info": {
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

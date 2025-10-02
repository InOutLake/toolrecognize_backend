import io
from PIL import Image
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
from .model import model, load_model, recognize
from .schemas import DetectResponse


@asynccontextmanager
async def lifespan(app):
    try:
        load_model()
    except Exception as e:
        print(f"Warning: Could not load model at startup: {e}")
        print("Model will be loaded on first request")
        raise Exception() from e
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

        detections = recognize(image)

        response = DetectResponse(
            detections=detections,
            total_detections=len(detections),
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

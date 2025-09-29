# YOLO Detection API

A simple FastAPI application that uses YOLO (You Only Look Once) for object detection in images.

## Features

- **Object Detection**: Uses YOLO model to detect objects in uploaded images
- **REST API**: Simple HTTP endpoints for image upload and detection
- **JSON Response**: Returns detection results in structured JSON format
- **Error Handling**: Comprehensive error handling for various scenarios

## Setup

1. **Install Dependencies**:
   ```bash
   cd recognize
   uv venv .venv
   uv pip install --python .venv/bin/python -r uv.lock
   ```

2. **Add YOLO Model**:
   - Place your trained YOLO model file as `model.pt` in the recognize directory
   - The app will automatically load the model on startup

## Usage

### Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8001`

### API Endpoints

#### Health Check
- **GET** `/`
- Returns API status and model loading status

#### Object Detection
- **POST** `/detect`
- **Body**: `multipart/form-data` with image file
- **Response**: JSON with detection results

### Example Usage

#### Using curl:
```bash
curl -X POST "http://localhost:8001/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg"
```

#### Using Python requests:
```python
import requests

url = "http://localhost:8001/detect"
with open("your_image.jpg", "rb") as image_file:
    files = {"file": ("image.jpg", image_file, "image/jpeg")}
    response = requests.post(url, files=files)
    result = response.json()
    print(result)
```

### Response Format

```json
{
  "success": true,
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.95,
      "bbox": {
        "x1": 100.0,
        "y1": 150.0,
        "x2": 300.0,
        "y2": 400.0
      }
    }
  ],
  "total_detections": 1,
  "image_info": {
    "width": 640,
    "height": 480,
    "mode": "RGB"
  }
}
```

## Testing

Run the test client:
```bash
python test_client.py
```

Make sure to have a test image file named `test_image.jpg` in the recognize directory.

## Docker

The recognize module is configured to run in Docker. The Dockerfile will:
1. Install all dependencies
2. Copy the application code
3. Run the FastAPI server on port 8001

## Notes

- The model file `model.pt` must be present in the recognize directory
- Supported image formats: JPEG, PNG, BMP, TIFF, etc.
- The API automatically converts images to RGB format for processing
- Detection results include bounding box coordinates, class names, and confidence scores

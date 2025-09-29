#!/usr/bin/env python3
"""
Test client for the YOLO Detection API
This script demonstrates how to use the /detect endpoint
"""

import requests
import json


def test_detection_api():
    """Test the YOLO detection API with a sample image"""
    url = "http://localhost:8001/detect"
    image_path = "test_image.jpg"

    try:
        health_url = "http://localhost:8001/"
        health_response = requests.get(health_url)
        print(f"API Health Check: {health_response.json()}")

        with open(image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            result = response.json()
            print("Detection Results:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except FileNotFoundError:
        print(f"Test image {image_path} not found. Please provide a test image.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Make sure the server is running on port 8001.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("YOLO Detection API Test Client")
    print("=" * 40)
    test_detection_api()

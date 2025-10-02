import asyncio
import os
import uvicorn
from src.worker import broker
from faststream import FastStream


if __name__ == "__main__":
    mode = os.getenv("RECOGNIZE_APP_MODE", "amqp")
    if mode == "amqp":
        app = FastStream(broker=broker)
        asyncio.run(app.run())

    elif mode == "http":
        uvicorn.run(
            "src.web_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
    else:
        raise ValueError("Mode value must be amqp or http")

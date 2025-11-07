from contextlib import asynccontextmanager
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, FastAPI
from infrastructure.repositories.broker import get_broker
import sys

from presentation.api import session_router
from core import SETTINGS


def include_routers(app: FastAPI, *routers: APIRouter) -> None:
    for router in routers:
        app.include_router(router)


def run_tests():
    import pytest

    exit_code = pytest.main(
        [
            "tests/",
            "-v",
            "--tb=short",
        ]
    )
    if exit_code != 0:
        print("Tests failed. Exiting.")
        sys.exit(exit_code)
    print("All tests passed!")


@asynccontextmanager
async def lifespan(app):
    try:
        if SETTINGS.recognize_app_mode == "amqp":
            await get_broker().start()

    except Exception as e:
        print(f"Warning: Could not startup: {e}")
    yield


app = FastAPI(title="Tools stacktaking control app", version="0.0.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# there is a bug and routers cannot be added nor in init lifespan function nor in main due to it
include_routers(
    app,
    session_router,
)


def main():
    if SETTINGS.debug:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach on port 5678...")
        debugpy.wait_for_client()

    if SETTINGS.test:
        run_tests()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["/app/src"],
    )


if __name__ == "__main__":
    main()

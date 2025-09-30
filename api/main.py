import asyncio
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, FastAPI
import sys

from src.api import (
    employee_router,
    session_router,
    tool_router,
    kit_router,
    location_router,
)
from src.database import seed
from src.core import SETTINGS

app = FastAPI(title="Tools stacktaking control app", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


include_routers(
    app,
    employee_router,
    session_router,
    tool_router,
    kit_router,
    location_router,
)


def main():
    if SETTINGS.debug:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        print("Waiting for debugger attach on port 5678...")
        debugpy.wait_for_client()

    if SETTINGS.test:
        run_tests()

    asyncio.run(seed())

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["/app/src"],
    )


if __name__ == "__main__":
    main()

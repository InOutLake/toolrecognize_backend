import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_analyze_service(monkeypatch):
    def _mock_analyze(tools):
        mock = MagicMock()
        mock.analyze.return_value = {"items": tools}
        return mock

    return _mock_analyze


KIT_TOOLS = [
    {"tool_name": "hammer", "quantity_required": 1},
    {"tool_name": "screwdriver", "quantity_required": 2},
    {"tool_name": "wrench", "quantity_required": 1},
]

RECOGNIZED_ALL = [
    {"tool_name": "hammer"},
    {"tool_name": "screwdriver"},
    {"tool_name": "wrench"},
]
RECOGNIZED_EXTRA = [
    {"tool_name": "hammer"},
    {"tool_name": "screwdriver"},
    {"tool_name": "wrench"},
    {"tool_name": "pliers"},
]
RECOGNIZED_MISSING = [
    {"tool_name": "hammer"},
]

SESSION_DATA = {
    "reciever_id": 1,
    "location_id": 1,
    "kit_id": 1,
}


# Test initialize_session
@pytest.mark.parametrize(
    "recognized_tools,desc",
    [
        (RECOGNIZED_ALL, "all tools present"),
        (RECOGNIZED_EXTRA, "extra tools present"),
        (RECOGNIZED_MISSING, "missing tools"),
    ],
)
def test_initialize_session(client, mock_analyze_service, recognized_tools, desc):
    # Patch AnalyzeServiceDep
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        "api.analyze.service.AnalyzeServiceDep",
        lambda: mock_analyze_service(recognized_tools),
    )
    files = {"image": ("test.jpg", b"fakeimage", "image/jpeg")}
    response = client.post("/session/", data=SESSION_DATA, files=files)
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    monkeypatch.undo()


# Test preclose_session
@pytest.mark.parametrize(
    "recognized_tools,desc",
    [
        (RECOGNIZED_ALL, "all tools present"),
        (RECOGNIZED_EXTRA, "extra tools present"),
        (RECOGNIZED_MISSING, "missing tools"),
    ],
)
def test_preclose_session(client, mock_analyze_service, recognized_tools, desc):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        "api.analyze.service.AnalyzeServiceDep",
        lambda: mock_analyze_service(recognized_tools),
    )
    files = {"image": ("test.jpg", b"fakeimage", "image/jpeg")}
    response = client.post("/session/1/preclose", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    monkeypatch.undo()


# Test list_sessions
def test_list_sessions(client):
    response = client.get("/session/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


# Test get_session_details
def test_get_session_details(client):
    # Assuming session_id 1 exists or is created by previous test
    response = client.get("/session/1")
    assert response.status_code in (200, 404)  # 404 if not found
    if response.status_code == 200:
        data = response.json()
        assert "status" in data


# Test open_session
def test_open_session(client):
    response = client.post("/session/1/open")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "status" in data


# Test close_session
def test_close_session(client):
    response = client.post("/session/1/close")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "status" in data

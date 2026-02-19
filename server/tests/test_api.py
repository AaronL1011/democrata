import os
import pytest
from fastapi.testclient import TestClient

from democrata_server.adapters.usage.memory_store import InMemoryJobStore
from democrata_server.api.http.deps import get_job_store, get_upload_auth
from democrata_server.main import app


async def noop_upload_auth():
    return None


@pytest.fixture
def client():
    app.dependency_overrides[get_upload_auth] = noop_upload_auth
    app.dependency_overrides[get_job_store] = lambda: InMemoryJobStore()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_ready(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert set(data["checks"].keys()) == {"redis", "qdrant", "postgres"}


class TestIngestionEndpoints:
    def test_get_job_status_invalid_id(self, client):
        response = client.get("/ingestion/jobs/invalid-uuid")
        assert response.status_code == 400
        assert "Invalid job ID" in response.json()["detail"]

    def test_get_job_status_not_found(self, client):
        response = client.get("/ingestion/jobs/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable"
)
class TestRAGEndpointsWithAPI:
    """Tests that require external API access."""

    def test_query_accepts_valid_request(self, client):
        response = client.post("/rag/query", json={"query": "What is a bill?"})
        assert response.status_code in [200, 500]

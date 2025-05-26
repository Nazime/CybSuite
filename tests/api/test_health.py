from cybsuite.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    """Test that the health check endpoint returns status ok"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}, "Health check should return status ok"

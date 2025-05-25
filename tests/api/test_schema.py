from fastapi.testclient import TestClient
from cybsuite.api.main import app

client = TestClient(app)

def test_list_schemas_contains_host():
    """Test that the list_schemas endpoint returns a list containing 'host'"""
    response = client.get("/api/v1/schema/request")
    assert response.status_code == 200
    schemas = response.json()
    assert isinstance(schemas, list), "Response should be a list"
    assert "host" in schemas, "Schema list should contain 'host'"
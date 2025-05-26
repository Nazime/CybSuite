from cybsuite.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_full_schema():
    """Test getting the complete schema"""
    response = client.get("/api/v1/schema/full")
    assert response.status_code == 200
    schema = response.json()
    assert isinstance(schema, dict), "Response should be a dictionary"
    names = [e['name'] for e in schema['entities']]
    assert "host" in names


def test_get_schema_names():
    """Test getting list of schema names"""
    response = client.get("/api/v1/schema/names")
    assert response.status_code == 200
    names = response.json()
    assert isinstance(names, list), "Response should be a list"
    assert "host" in names, "Schema list should contain 'host'"


def test_get_entity_schema():
    """Test getting schema details for a specific entity"""
    response = client.get("/api/v1/schema/entity/host")
    assert response.status_code == 200
    entity = response.json()
    assert isinstance(entity, dict), "Response should be a dictionary"
    assert "fields" in entity, "Entity should contain fields"
    assert "hostname" in entity['fields']


def test_get_entity_schema_not_found():
    """Test getting schema details for a non-existent entity"""
    response = client.get("/api/v1/schema/entity/nonexistent")
    assert response.status_code == 404


def test_get_entity_field_names():
    """Test getting field names for an entity"""
    response = client.get("/api/v1/schema/entity/host/names")
    assert response.status_code == 200
    names = response.json()
    assert isinstance(names, list), "Response should be a list"
    assert len(names) > 0, "Field names list should not be empty"
    assert "hostname" in names, "Host entity should have hostname field"


def test_get_entity_field_names_not_found():
    """Test getting field names for a non-existent entity"""
    response = client.get("/api/v1/schema/entity/nonexistent/names")
    assert response.status_code == 404


def test_get_field_schema():
    """Test getting details for a specific field"""
    response = client.get("/api/v1/schema/field/host/hostname")
    assert response.status_code == 200
    field = response.json()
    assert isinstance(field, dict), "Response should be a dictionary"


def test_get_field_schema_not_found():
    """Test getting a non-existent field"""
    response = client.get("/api/v1/schema/field/host/nonexistent")
    assert response.status_code == 404


def test_get_field_schema_entity_not_found():
    """Test getting a field from a non-existent entity"""
    response = client.get("/api/v1/schema/field/nonexistent/field")
    assert response.status_code == 404

from cybsuite.cyberdb import cyberdb_schema
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/schema", tags=["Schema"])


@router.get("/full")
async def get_full_schema() -> Dict[str, Any]:
    """Get complete schema details for all entities"""
    return cyberdb_schema.to_json()


@router.get("/names", response_model=List[str])
async def get_schema_names() -> List[str]:
    """Get a list of all available schema names"""
    return [e.name for e in cyberdb_schema]


@router.get("/entity/{entity}")
async def get_entity_schema(entity: str) -> Dict[str, Any]:
    """Get the detailed schema definition for a given entity"""
    try:
        return cyberdb_schema[entity].to_json()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Entity '{entity}' not found")


@router.get("/entity/{entity}/names", response_model=List[str])
async def get_entity_field_names(entity: str) -> List[str]:
    """Get list of field names for a given entity"""
    try:
        entity_schema = cyberdb_schema[entity]
        return [e.name for e in entity_schema]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Entity '{entity}' not found")


@router.get("/field/{entity}/{field}")
async def get_field_schema(entity: str, field: str) -> Dict[str, Any]:
    """Get details for a specific field in an entity"""
    try:
        entity_schema = cyberdb_schema[entity]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Entity '{entity}' not found")

    try:
        return entity_schema[field].to_json()
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Field '{field}' not found in entity '{entity}'",
        )

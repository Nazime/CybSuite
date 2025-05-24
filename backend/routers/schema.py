from fastapi import APIRouter, HTTPException
from cybsuite.cyberdb import cyberdb_schema

router = APIRouter(
    prefix="/schema",
    tags=["Schema"]
)

@router.get("/request")
async def list_schemas():
    """Get a list of all available schema names"""
    return [e.name for e in cyberdb_schema]

@router.get("/detail/{schema_name}")
async def get_schema_detail(schema_name: str):
    """Get the detailed schema definition for a given table"""
    try:
        return cyberdb_schema[schema_name].to_json()
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Schema '{schema_name}' not found"
        )
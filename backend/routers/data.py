from fastapi import APIRouter, Depends, Query, HTTPException
from cybsuite.cyberdb import CyberDB
from asgiref.sync import sync_to_async
from typing import Optional, Dict, Any, List
from functools import partial

router = APIRouter(
    prefix="/data",
    tags=["Data Operations"],
)

def get_db():
    """Get CyberDB instance"""
    db = CyberDB.from_default_config()
    return db

def serialize_model(item):
    """Synchronously serialize a Django model instance"""
    return {
        field.name: getattr(item, field.name)
        for field in item._meta.fields
    }

async def async_request(db: CyberDB, table_name: str, skip: int = 0, limit: Optional[int] = None):
    """Async wrapper for db.request"""
    try:
        # Get the queryset synchronously
        queryset = await sync_to_async(db.request)(table_name)

        # Apply skip and limit using Django slicing
        if limit:
            queryset = queryset[skip:skip + limit]
        else:
            queryset = queryset[skip:]

        # Convert QuerySet to list synchronously
        items = await sync_to_async(list)(queryset)

        # Serialize each model instance synchronously
        serialized_items = []
        for item in items:
            serialized = await sync_to_async(serialize_model)(item)
            serialized_items.append(serialized)

        return serialized_items

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data: {str(e)}"
        )

async def async_detail(db: CyberDB, table_name: str, obj_id: int):
    """Async wrapper for db.first"""
    try:
        # Get the object synchronously
        obj = await sync_to_async(db.first)(table_name, id=obj_id)
        if obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {obj_id} not found in table {table_name}"
            )

        # Serialize the object synchronously
        return await sync_to_async(serialize_model)(obj)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching object: {str(e)}"
        )

@router.get("/request/{table_name}")
async def get_table_data(
    table_name: str,
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, gt=0),
    db: CyberDB = Depends(get_db)
):
    """Get records from a table with optional skip and limit"""
    return await async_request(db, table_name, skip=skip, limit=limit)

@router.get("/detail/{table_name}/{obj_id}")
async def get_object_detail(
    table_name: str,
    obj_id: int,
    db: CyberDB = Depends(get_db)
):
    """Get a single object by its ID"""
    return await async_detail(db, table_name, obj_id)
from fastapi import APIRouter, Depends, Query, HTTPException
from cybsuite.cyberdb import CyberDB
from asgiref.sync import sync_to_async
from typing import Optional, Dict, Any, List
from functools import partial
from django.db.models import Q
import operator
from functools import reduce
import json

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

async def async_request(db: CyberDB, table_name: str, skip: int = 0, limit: Optional[int] = None, search: Optional[str] = None, filters: Optional[str] = None):
    """Async wrapper for db.request"""
    try:
        # Get the queryset synchronously
        queryset = await sync_to_async(db.request)(table_name)

        # Apply column filters if provided
        if filters:
            try:
                filter_dict = json.loads(filters)
                for field, value in filter_dict.items():
                    if value:  # Only apply non-empty filters
                        queryset = queryset.filter(**{f"{field}__icontains": value})
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid filters format"
                )

        # Apply global search if provided
        if search:
            # Get all fields from the model
            model_fields = queryset.model._meta.fields

            # Create a Q object for each field to search in
            q_objects = []
            for field in model_fields:
                # Only search in text and number fields
                if field.get_internal_type() in ['CharField', 'TextField', 'IntegerField', 'FloatField', 'DecimalField']:
                    q_objects.append(Q(**{f"{field.name}__icontains": search}))

            # Combine all Q objects with OR operator
            if q_objects:
                queryset = queryset.filter(reduce(operator.or_, q_objects))

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

async def async_delete(db: CyberDB, table_name: str, obj_id: int):
    """Async wrapper for deleting an object"""
    try:
        # Get the object synchronously
        obj = await sync_to_async(db.first)(table_name, id=obj_id)
        if obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {obj_id} not found in table {table_name}"
            )

        # Delete the object
        await sync_to_async(obj.delete)()

        return {"status": "success", "message": f"Object {obj_id} from table {table_name} has been deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting object: {str(e)}"
        )

async def async_feed(db: CyberDB, table_name: str, data: Dict[str, Any]):
    """Async wrapper for db.feed"""
    try:
        # Perform the feed operation
        obj = await sync_to_async(db.feed)(table_name, **data)

        # Serialize the resulting object
        return await sync_to_async(serialize_model)(obj)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error feeding object: {str(e)}"
        )

@router.get("/request/{table_name}")
async def get_table_data(
    table_name: str,
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, gt=0),
    search: Optional[str] = Query(None),
    filters: Optional[str] = Query(None),
    db: CyberDB = Depends(get_db)
):
    """Get records from a table with optional skip, limit, search and column filters"""
    return await async_request(db, table_name, skip=skip, limit=limit, search=search, filters=filters)

@router.get("/detail/{table_name}/{obj_id}")
async def get_object_detail(
    table_name: str,
    obj_id: int,
    db: CyberDB = Depends(get_db)
):
    """Get a single object by its ID"""
    return await async_detail(db, table_name, obj_id)

@router.delete("/detail/{table_name}/{obj_id}")
async def delete_object(
    table_name: str,
    obj_id: int,
    db: CyberDB = Depends(get_db)
):
    """Delete a single object by its ID"""
    return await async_delete(db, table_name, obj_id)

@router.post("/feed/{table_name}")
async def feed_object(
    table_name: str,
    data: Dict[str, Any],
    db: CyberDB = Depends(get_db)
):
    """Create or update an object in the specified table
    If an 'id' is provided in the data, it will update the existing object
    Otherwise, it will create a new object
    """
    return await async_feed(db, table_name, data)
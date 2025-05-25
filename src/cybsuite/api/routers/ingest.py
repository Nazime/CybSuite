from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
from cybsuite.cyberdb import CyberDB, pm_ingestors
from asgiref.sync import sync_to_async

router = APIRouter(
    prefix="/ingest",
    tags=["Data Ingestion"],
)

def get_db():
    """Get CyberDB instance"""
    db = CyberDB.from_default_config()
    return db

@router.get("/plugins")
async def list_ingestors() -> List[Dict[str, Any]]:
    """
    Get a list of all available data ingestors
    Returns a list of ingestor configurations and their metadata
    """
    return [{"name": plugin.name} for plugin in pm_ingestors]

@router.post("/{ingestor_name}")
async def ingest_data(
    ingestor_name: str,
    file: UploadFile = File(...),
    db: CyberDB = Depends(get_db)
) -> Dict[str, Any]:
    """
    Ingest data using the specified ingestor plugin
    Args:
        ingestor_name: Name of the ingestor plugin to use
        file: File to ingest
    Returns:
        Status of the ingestion operation
    """
    try:
        # Read file content
        content = await file.read()

        # Get the ingestor plugin
        ingestor = pm_ingestors[ingestor_name](db)

        # Run the ingestor (wrapped in sync_to_async since it might be synchronous)
        result = await sync_to_async(ingestor.ingest)(content)

        return {
            "status": "success",
            "message": f"Data ingested successfully using {ingestor_name}",
            "details": result
        }

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Ingestor '{ingestor_name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting data: {str(e)}"
        )
    finally:
        await file.close()
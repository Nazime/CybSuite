from typing import Any, Dict, List

from cybsuite.cyberdb import pm_ingestors, pm_reporters
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/plugins",
    tags=["Plugins Operations"],
)


@router.get("/reporters")
async def get_reporters() -> List[Dict[str, Any]]:
    """
    Get a list of all available reporters
    Returns a list of reporter configurations and their metadata
    """
    # This is a placeholder - you will implement the actual logic
    return [{"name": plugin.name} for plugin in pm_reporters]


@router.get("/ingestors")
async def get_ingestors() -> List[Dict[str, Any]]:
    """
    Get a list of all available ingestors
    Returns a list of ingestor configurations and their metadata
    """
    return [{"name": plugin.name} for plugin in pm_ingestors]

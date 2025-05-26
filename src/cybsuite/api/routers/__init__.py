from fastapi import APIRouter

from .data import router as data_router
from .ingest import router as ingest_router
from .plugins import router as plugins_router
from .report import router as report_router
from .schema import router as schema_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(data_router)
router.include_router(schema_router)
router.include_router(plugins_router)
router.include_router(report_router)
router.include_router(ingest_router)

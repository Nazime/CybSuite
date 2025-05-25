from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from models import Base
# from database import engine
from routers import router as api_router

# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Host Management API",
    description="API for managing hosts and services with data ingestion capabilities",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include root API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Host Management API",
        "version": "1.0.0",
        "endpoints": {
            "data_request": "/api/v1/data/request/<table_name>",
            "data_detail": "/api/v1/data/detail/<table_name>/<object_id>",
            "ingest": "/api/v1/ingest/<plugin_name>",
        },
    }

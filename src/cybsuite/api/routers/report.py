from typing import Any, Dict, List

from asgiref.sync import sync_to_async
from cybsuite.cyberdb import CyberDB, pm_reporter
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/report",
    tags=["Report Operations"],
)


def get_db():
    """Get CyberDB instance"""
    db = CyberDB.from_default_config()
    return db


@router.get("/{reporter_name}")
async def generate_report(reporter_name: str, db: CyberDB = Depends(get_db)) -> Any:
    """
    Generate a report using the specified reporter and return it as a downloadable file
    Args:
        reporter_name: Name of the reporter plugin to use
    Returns:
        FileResponse containing the generated report
    """
    import os
    import tempfile

    from fastapi.background import BackgroundTasks
    from fastapi.responses import FileResponse

    try:
        # Create temporary file
        reporter = pm_reporter[reporter_name](db)
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=reporter.extension
        ) as tmp_file:
            temp_path = tmp_file.name

        # Wrap the synchronous run method with sync_to_async
        await sync_to_async(reporter.run)(temp_path)

        # Create background task to cleanup temp file
        background_tasks = BackgroundTasks()
        background_tasks.add_task(os.unlink, temp_path)

        # Set media type based on extension
        media_type = (
            "text/html" if reporter.extension == ".html" else "application/json"
        )

        # Return the file as a downloadable response
        return FileResponse(
            path=temp_path,
            filename=f"report_{reporter_name}{reporter.extension}",
            media_type=media_type,
            background=background_tasks,
        )

    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Reporter '{reporter_name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )

import os
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from mimetypes import guess_type

omics_router = APIRouter() #FastAPI(title="Precious json server", version="0.1", description="API server to serve jsons", debug=True)
file_directory = Path(os.path.abspath(__file__)).parent.parent.resolve() / "omics"

# Serve static files directly from the directory
#omics_router.mount("/omics", StaticFiles(directory=str(file_directory)), name="files")

@omics_router.get("/omics/{filename}")
async def download_file(filename: str):
    file_path = file_directory / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(path=file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")


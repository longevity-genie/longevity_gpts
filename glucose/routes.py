from fastapi import APIRouter

glucose_router = APIRouter() #FastAPI(title="Anage rest", version="0.1", description="API server to handle queries to restful_anage", debug=True)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from mimetypes import guess_type

# Define the path to the folder
file_directory = Path("./glucose/files")

# Serve static files directly from the directory
glucose_router.mount("/files", StaticFiles(directory=str(file_directory)), name="files")

@glucose_router.get("download/{filename}")
async def download_file(filename: str):
    file_path = file_directory / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(path=file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@glucose_router.get("view/{filename}")
async def view_file(filename: str):
    file_path = file_directory / filename
    if file_path.exists() and file_path.is_file():
        mime_type, _ = guess_type(str(file_path))
        if mime_type and mime_type.startswith("image"):
            return FileResponse(path=file_path, media_type=mime_type)
        else:
            raise HTTPException(status_code=400, detail="File is not an image")
    else:
        raise HTTPException(status_code=404, detail="File not found")


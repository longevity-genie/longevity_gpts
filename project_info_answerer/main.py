from pathlib import Path

from fastapi import APIRouter

project_info_router = APIRouter()


@project_info_router.get("/")
def read_root():
    return "This is REST API for Project Description Information."


@project_info_router.get("/project_info", description="Returns information about the Longevity Genie project.")
def project_info():
    """Returns information about the Longevity Genie project."""
    result = ""
    with open(Path(Path(__file__).parent, "data", "project_description.txt")) as f:
        result = f.read()
    return result

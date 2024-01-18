# TODO with ideas from https://fastapi.tiangolo.com/tutorial/bigger-applications/ import routes of submodules
import torch
from fastapi import APIRouter
from langchain_community.embeddings import HuggingFaceEmbeddings


from literature.models import *
from fastapi.responses import FileResponse
core_router = APIRouter()

current_file_dir = Path(__file__).parent
current_dir = current_file_dir if (current_file_dir / 'privacy_policy.md').exists() else current_file_dir.parent


@core_router.get("/privacy-policy")
async def privacy_policy():
    privacy_policy_path = current_dir / 'privacy_policy.md'
    print("DIR IS " + str(privacy_policy_path))
    return FileResponse(str(privacy_policy_path))


@core_router.get("/terms")
async def terms_of_service():
    terms_of_service_path = current_dir / "terms_of_service.md"
    print("DIR IS " + str(terms_of_service_path))
    return FileResponse(str(terms_of_service_path))
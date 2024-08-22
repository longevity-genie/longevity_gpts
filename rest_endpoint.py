#!/usr/bin/env python
import re

import loguru
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.models import ExternalDocumentation
from fastapi.openapi.utils import get_openapi
from hybrid_search.opensearch_hybrid_search import *
from pycomfort.config import load_environment_keys
from pydantic_core import Url
from starlette.middleware.cors import CORSMiddleware

import blood.routes
import genetics.main
import gpt.routes
import literature.routes
from core.routes import core_router
from dotenv import load_dotenv
load_dotenv("clinical_trials/.env")
import clinical_trials.clinical_trails_router

load_environment_keys(usecwd=True)


expires = os.getenv("EXPIRES", 3600)

loguru.logger.add("logs/longevity_gpts.log", rotation="10 MB")


env_embed_model= os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")


app = FastAPI(
    # Initialize FastAPI cache with in-memory backend
    title="Restful longevity genie server",
    version="0.1",
    description="API server to handle queries to restful_genie",
    debug=True
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(core_router) # basic stuff
app.include_router(literature.routes.literature_router) # literature hybrid search API
app.include_router(gpt.routes.gpt_router) # longevity GPT API
app.include_router(blood.routes.bloody_router) # blood API
app.include_router(genetics.main.genetics_router)
app.include_router(clinical_trials.clinical_trails_router.clinical_trails_router)

hosts_str = os.getenv('HOSTS')
port = int(os.getenv("PORT", 8000))
port_part = ':' + str(port) if port is not None else ''

hosts = hosts_str.split(",") if hosts_str is not None else ["http://0.0.0.0"]
main_host = hosts[0]
servers = [{"url": h} for h in hosts]

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Longevity Genie and restful_genie REST API",
        version="0.0.13",
        description="This REST service provides means for semantic search in scientific literature and downloading papers",
        terms_of_service=f"{main_host}/terms/",
        routes=app.routes,
    )
    openapi_schema["servers"] = servers
    """
    openapi_schema["externalDocs"] = ExternalDocumentation(
        description="Privacy Policy",
        url=f"{main_host}/privacy-policy"  # Use a string instead of Url object
    ).model_dump()
    """
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "This is REST API is for Longevity Genie, please use /docs subpath to see swagger documentation"}


@app.get("/version", description="return the version of the current restful_genie project", response_model=str)
async def version():
    return '0.0.15'


if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=port)

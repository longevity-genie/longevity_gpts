import os

import loguru
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi
import sqlite3

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from typing_extensions import Annotated
from pycomfort.config import load_environment_keys

load_environment_keys(usecwd=True)

loguru.logger.add("clinical_trials.log", rotation="10 MB")

API_KEY_NAME = "x-api-key"
API_KEY = os.getenv("API_KEY", "")

clinical_trails_router = APIRouter()
sql_path = "data/studies_db.sqlite"

def api_key_auth(api_key: str = Depends(APIKeyHeader(name=API_KEY_NAME))):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@clinical_trails_router.get("/")
def clinical_trails_root():
    return "This is REST API for clinical trails gpt."

@clinical_trails_router.get("/process_sql/{sql}", description="Executes sql query and returns results for clinical tails database.")
def process_sql(dependencies: Annotated[str, Depends(api_key_auth)], sql:str):
    conn = sqlite3.connect(sql_path, isolation_level='DEFERRED')
    cursor = conn.cursor()
    cursor.execute(sql)
    try:
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            conn.close()
            return ""
        names = [description[0] for description in cursor.description]
        text = "; ".join(names)+"\n"
        for row in rows:
            row = [str(i) for i in row]
            text += "; ".join(row)+"\n"
    finally:
        conn.close()

    return text


def custom_openapi():
    if clinical_trails_router.openapi_schema:
        return clinical_trails_router.openapi_schema
    openapi_schema = get_openapi(
        title="Clinical trails REST API",
        version="0.1",
        description="",
        terms_of_service="https://agingkills.eu/terms/",
        routes=clinical_trails_router.routes,
    )

    openapi_schema["servers"] = [{"url": "https://clinical-trials.longevity-genie.info"}, {"url": "https://localhost:8085"}]
    clinical_trails_router.openapi_schema = openapi_schema
    return clinical_trails_router.openapi_schema

clinical_trails_router.openapi = custom_openapi
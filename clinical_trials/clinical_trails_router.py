import os

import loguru
from loguru import logger
from fastapi import APIRouter

import sqlite3
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from typing_extensions import Annotated
from pycomfort.config import load_environment_keys

from pathlib import Path

class Item(BaseModel):
    sql: str

load_environment_keys(usecwd=True)

loguru.logger.add("clinical_trials.log", rotation="10 MB")

API_KEY_NAME = "x-api-key"
API_KEY = os.getenv("API_KEY", "")

clinical_trails_router = APIRouter()
clinical_trials_sql_path = "data/studies_db.sqlite"
clinical_trials_data_path = "data/"

def set_prefix_clinical_trials_sql_path(prefix:str):
    global clinical_trials_sql_path
    clinical_trials_sql_path = prefix + clinical_trials_sql_path

def set_prefix_clinical_trials_data_path(prefix:str):
    global clinical_trials_data_path
    clinical_trials_data_path = prefix + clinical_trials_data_path

def api_key_auth(api_key: str = Depends(APIKeyHeader(name=API_KEY_NAME))):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@clinical_trails_router.get("/")
def clinical_trails_root():
    return "This is REST API for clinical trails gpt."


@clinical_trails_router.get("/info/", description="Return information about database and its date.")
def clinical_trails_info():
    path:Path = Path(clinical_trials_data_path + "xml/Contents.txt")
    if path.exists():
        with open(path) as f:
            return f.read()


@clinical_trails_router.get("/full_trial/{study_id}", description="Return full trial text in xml.")
def clinical_trails_full_trial(study_id:str):
    conn = sqlite3.connect(clinical_trials_sql_path, isolation_level='DEFERRED')
    cursor = conn.cursor()
    cursor.execute(f"SELECT path FROM studies WHERE study_id = '{study_id}'")
    path = cursor.fetchone()
    conn.close()
    if path is None or len(path) == 0:
        return "No data"
    path = path[0].replace('\\', '/')
    with open(clinical_trials_data_path + path) as f:
        return f.read()


@clinical_trails_router.post("/process_sql/", description="Executes sql query and returns results for clinical trials database.")
def process_sql(dependencies: Annotated[str, Depends(api_key_auth)], item:Item):
    conn = sqlite3.connect(clinical_trials_sql_path, isolation_level='DEFERRED')
    cursor = conn.cursor()
    cursor.execute(item.sql)
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





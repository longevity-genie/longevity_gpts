from pathlib import Path
from typing import Optional

import loguru
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel


class QueryPaper(BaseModel):
    text: Optional[str] = None
    collection_name: str = "bge_base_en_v1.5_aging_5"
    limit: int = 10

    db: Optional[str] = None #for opensearch should be URL
    #doi: Optional[str] = None
    #with_vectors: bool = False
    #with_payload: bool = True

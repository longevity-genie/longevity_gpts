from pathlib import Path
from typing import Optional

import loguru
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel


class QueryPaper(BaseModel):
    text: Optional[str] = None
    collections: list[str] = ["aging_papers_paragraphs_bge_base_en_v1.5", "aging_papers_paragraphs_specter2"]
    limit: int = 10
    db: Optional[str] = "https://localhost:9200"
    verbose: bool = False
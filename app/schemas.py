from typing import List
from pydantic import BaseModel

class Commit(BaseModel):
    commit: str
    author: str
    date: str
    message: str
    files_changed: int
    lines_added: int
    lines_deleted: int
    branches: List[str]
    tags: List[str]

class PRGenerationRequest(BaseModel):
    commits: List[Commit]
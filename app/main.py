import logging

from typing import Union

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

app = FastAPI()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

@app.post("/pr_generation")
def pr_generation(requset: Request, commits: Union[list, None] = None):

    logger.debug("Received request for PR generation with commits: %s", commits)


    return {"title": "Test PR",
            "body": "This is a test PR body",}
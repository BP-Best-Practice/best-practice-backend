import logging

from fastapi import FastAPI
from .schemas import Commit, PRGenerationRequest

app = FastAPI()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
print("Logger initialized:", logger)

@app.post("/pr_generation")
def pr_generation(request: PRGenerationRequest):

    logger.debug("Received request for PR generation with commits: %s", request.commits)
    print("Received commits:", request.commits)

    return {"title": "Test PR",
            "body": "This is a test PR body",}
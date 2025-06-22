import logging

from fastapi import FastAPI
from .schemas import Commit, PRGenerationRequest

app = FastAPI()

logging.basicConfig(
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.post("/pr_generation")
def pr_generation(request: PRGenerationRequest):

    for commit in request.commits:
        if not isinstance(commit, Commit):
            logging.error("Invalid commit data: %s", commit)
            raise ValueError("올바른 커밋 데이터가 아닙니다.")
        
        recommended_pr = pr_generation_handler([commit])
    
        logger.debug("Recommended PR: %s", recommended_pr)

    logging.debug("Received PR generation request with %d commits", len(request.commits))
    return recommended_pr

def pr_generation_handler(commits: list[Commit]):
    logging.info("Generating PR with %d commits", len(commits))
    return {"title": "Test PR",
            "body": "This is a test PR body",}
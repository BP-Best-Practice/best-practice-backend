import os
import logging
import requests

from fastapi import FastAPI
from .schemas import Commit, PRGenerationRequest
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

logging.basicConfig(
    filename="app/app.log",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Starting FastAPI application")

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

@app.get("/repos")
def get_repos() -> dict:
    logging.info("Fetching repositories")

    github_uri = "https://api.github.com"
    path = "/user/repos"

    user_token = os.getenv("GITHUB_TOKEN")
    if not user_token:
        logging.error("GITHUB_TOKEN not found in environment variables")
        raise EnvironmentError("GITHUB_TOKEN not found in environment variables")
    headers = {
        "Authorization": f"Bearer {user_token}",
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.get(github_uri + path, headers=headers)

    if response.status_code != 200:
        logging.error("Failed to fetch repositories: %s", response.text)
        raise ConnectionError(f"Failed to fetch repositories: {response.status_code}")
    logging.info("Successfully fetched repositories")
    

    response = {
        "status_code": response.status_code,
        "data": response.json()
    }

    return response

@app.get("/commits/{repository_name}")
def get_commits(repository_name: str) -> dict:
    logging.info("Fetching commits")

    print(f"Repository name: {repository_name}")

    github_uri = "https://api.github.com"

    owner = os.getenv("GITHUB_REPO_OWNER")
    # owner = "cookiemiro"

    print(f"Repository owner: {owner}")

    logging.debug("Repository owner: %s", owner)

    # if not repository_name or not owner:
    #     logging.error("GITHUB_REPO_NAME or GITHUB_REPO_OWNER not found in environment variables")
    #     raise EnvironmentError("GITHUB_REPO_NAME or GITHUB_REPO_OWNER not found in environment variables")
   
    path = f"/repos/{owner}/{repository_name}/commits"

    user_token = os.getenv("GITHUB_TOKEN")
    if not user_token:
        logging.error("GITHUB_TOKEN not found in environment variables")
        raise EnvironmentError("GITHUB_TOKEN not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {user_token}",
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    response = requests.get(github_uri + path, headers=headers, timeout=10)

    if response.status_code != 200:
        logging.error("Failed to fetch commits: %s", response.text)
        raise ConnectionError(f"Failed to fetch commits: {response.status_code}")
    logging.info("Successfully fetched commits")
    

    response = {
        "status_code": response.status_code,
        "data": response.json()
    }

    return response
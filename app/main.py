import os
import logging

from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import Commit, PRGenerationRequest
from .database import get_db, engine
from .models import Base
from .services.github_service import GitHubService
from .services.user_service import UserService
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

logging.basicConfig(
    filename="app/app.log",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.post("/pr_generation")
def pr_generation(
    request: PRGenerationRequest, 
    db: Session = Depends(get_db)
):
    """PR 생성 요청 처리"""
    try:
        for commit in request.commits:
            if not isinstance(commit, Commit):
                logging.error("Invalid commit data: %s", commit)
                raise ValueError("올바른 커밋 데이터가 아닙니다.")
            
        recommended_pr = pr_generation_handler(request.commits)
        logger.debug("Recommended PR: %s", recommended_pr)
        
        # PR 생성 기록을 데이터베이스에 저장하는 로직 추가 가능
        
        return recommended_pr
        
    except Exception as e:
        logger.error(f"PR generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repos/{user_id}")
def get_repos(user_id: int, db: Session = Depends(get_db)) -> dict:
    """사용자의 저장소 목록 조회"""
    #try:
    github_service = GitHubService(db)
    return github_service.get_user_repos(user_id)
        
    # except ValueError as e:
    #     logger.error(f"User validation error: {e}")
    #     raise HTTPException(status_code=400, detail=str(e))
    # except ConnectionError as e:
    #     logger.error(f"GitHub API error: {e}")
    #     raise HTTPException(status_code=502, detail=str(e))
    # except Exception as e:
    #     logger.error(f"Unexpected error: {e}")
    #     raise HTTPException(status_code=500, detail="내부 서버 오류")

@app.get("/commits/{user_id}/{owner}/{repository_name}")
def get_commits(
    user_id: int, 
    owner: str, 
    repository_name: str, 
    db: Session = Depends(get_db)
) -> dict:
    """저장소의 커밋 목록 조회"""
    try:
        github_service = GitHubService(db)
        return github_service.get_commits(user_id, owner, repository_name)
        
    except ValueError as e:
        logger.error(f"User validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

def pr_generation_handler(commits: list[Commit]):
    """PR 생성 핸들러"""
    logging.info("Generating PR with %d commits", len(commits))
    return {
        "title": "Test PR",
        "body": "This is a test PR body",
    }
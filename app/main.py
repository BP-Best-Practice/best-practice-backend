import os
import logging

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .schemas import Commit, PRGenerationRequest
from .database import get_db, engine
from .models import Base
from .services.github_service import GitHubService
from .services.repository_service import RepositoryService
from .services.user_service import UserService
from .services.commit_history_service import CommitHistoryService
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
def get_repos(
    user_id: int, 
    force_refresh: bool = False,
    include_archived: bool = False,
    db: Session = Depends(get_db)
) -> dict:
    """사용자의 저장소 목록 조회 (ETag 캐싱 적용)"""
    try:
        github_service = GitHubService(db)
        result = github_service.get_user_repos(user_id, force_refresh=force_refresh)
        
        # 아카이브된 저장소 필터링
        if not include_archived and 'data' in result:
            result['data'] = [
                repo for repo in result['data'] 
                if not repo.get('archived', False)
            ]
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/repos/{user_id}/{repo_id}/favorite")
def toggle_favorite_repository(
    user_id: int,
    repo_id: int,
    db: Session = Depends(get_db)
):
    """
        저장소 즐겨찾기 토글
    """
    repo_service = RepositoryService(db)
    is_favorited = repo_service.toggle_favorite(user_id, repo_id)
    
    return {
        "repository_id": repo_id,
        "is_favorited": is_favorited
    }

@app.get("/commits/{user_id}/{owner}/{repository_name}")
def get_commits(
    user_id: int, 
    owner: str, 
    repository_name: str,
    save_to_history: bool = Query(True, description="커밋 히스토리 저장 여부"),
    per_page: int = Query(30, ge=1, le=100, description="페이지당 커밋 수"),
    db: Session = Depends(get_db)
) -> dict:
    """저장소의 커밋 목록 조회 및 히스토리 저장"""
    try:
        github_service = GitHubService(db)
        return github_service.get_commits(
            user_id,
            owner,
            repository_name, 
            save_to_history=save_to_history, 
            per_page=per_page
        )
        
    except ValueError as e:
        logger.error(f"User validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@app.get("/commits/{user_id}/{owner}/{repository_name}/{commit_sha}")
def get_commit_details(
    user_id: int,
    owner: str,
    repository_name: str,
    commit_sha: str,
    save_to_history: bool = Query(True, description="커밋 히스토리 저장 여부"),
    db: Session = Depends(get_db)
) -> dict:
    """특정 커밋의 상세 정보 조회"""
    try:
        github_service = GitHubService(db)
        return github_service.get_commit_details(
            user_id, owner, repository_name, commit_sha,
            save_to_history=save_to_history
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@app.get("/history/commits/{user_id}/{repository_name}")
def get_commit_history(
    user_id: int,
    repository_name: str,
    limit: int = Query(100, ge=1, le=500, description="조회할 커밋 수"),
    author_email: Optional[str] = Query(None, description="작성자 이메일로 필터링"),
    days: Optional[int] = Query(None, ge=1, le=365, description="최근 N일 이내 커밋만 조회"),
    db: Session = Depends(get_db)
) -> dict:
    """저장된 커밋 히스토리 조회"""
    try:
        # 저장소 정보 조회
        repo_service = RepositoryService(db)
        repo = repo_service.get_repository_by_name(user_id, repository_name)
        if not repo:
            raise HTTPException(status_code=404, detail="저장소를 찾을 수 없습니다.")
        
        commit_service = CommitHistoryService(db)
        
        # 조건에 따라 다른 쿼리 실행
        if author_email:
            commits = commit_service.get_commits_by_author(repo.id, author_email, limit)
        elif days:
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            commits = commit_service.get_commits_by_date_range(repo.id, start_date, end_date)
        else:
            commits = commit_service.get_repository_commits(repo.id, limit)
        
        # 응답 형식 변환
        commit_data = []
        for commit in commits:
            commit_data.append({
                "sha": commit.commit_sha,
                "message": commit.commit_message,
                "author": {
                    "name": commit.author_name,
                    "email": commit.author_email
                },
                "committed_at": commit.committed_at.isoformat() if commit.committed_at else None,
                "files_changed": commit.files_changed or [],
                "stats": {
                    "additions": commit.additions or 0,
                    "deletions": commit.deletions or 0,
                    "file_count": commit.file_count or 0
                },
                "cached_at": commit.cached_at.isoformat() if commit.cached_at else None
            })
        
        return {
            "status_code": 200,
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name
            },
            "commits": commit_data,
            "total_count": len(commit_data),
            "filters": {
                "author_email": author_email,
                "days": days,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get commit history: {e}")
        raise HTTPException(status_code=500, detail="커밋 히스토리 조회 실패")

@app.get("/history/stats/{user_id}/{repository_name}")
def get_commit_stats(
    user_id: int,
    repository_name: str,
    db: Session = Depends(get_db)
) -> dict:
    """저장소 커밋 통계 조회"""
    try:
        repo_service = RepositoryService(db)
        repo = repo_service.get_repository_by_name(user_id, repository_name)
        if not repo:
            raise HTTPException(status_code=404, detail="저장소를 찾을 수 없습니다.")
        
        commit_service = CommitHistoryService(db)
        stats = commit_service.get_commits_stats(repo.id)
        
        return {
            "status_code": 200,
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name
            },
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get commit stats: {e}")
        raise HTTPException(status_code=500, detail="커밋 통계 조회 실패")

@app.get("/history/activity/{user_id}/{repository_name}")
def get_recent_activity(
    user_id: int,
    repository_name: str,
    days: int = Query(7, ge=1, le=30, description="최근 N일간의 활동"),
    db: Session = Depends(get_db)
) -> dict:
    """최근 활동 요약 조회"""
    try:
        repo_service = RepositoryService(db)
        repo = repo_service.get_repository_by_name(user_id, repository_name)
        if not repo:
            raise HTTPException(status_code=404, detail="저장소를 찾을 수 없습니다.")
        
        commit_service = CommitHistoryService(db)
        activity = commit_service.get_recent_activity(repo.id, days)
        
        return {
            "status_code": 200,
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name
            },
            "period_days": days,
            "activity": activity,
            "total_commits": len(activity)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent activity: {e}")
        raise HTTPException(status_code=500, detail="최근 활동 조회 실패")

@app.delete("/history/cleanup/{user_id}/{repository_name}")
def cleanup_old_commits(
    user_id: int,
    repository_name: str,
    days_to_keep: int = Query(30, ge=7, le=365, description="보관할 일수"),
    db: Session = Depends(get_db)
) -> dict:
    """오래된 커밋 히스토리 정리"""
    try:
        repo_service = RepositoryService(db)
        repo = repo_service.get_repository_by_name(user_id, repository_name)
        if not repo:
            raise HTTPException(status_code=404, detail="저장소를 찾을 수 없습니다.")
        
        commit_service = CommitHistoryService(db)
        deleted_count = commit_service.cleanup_old_commits(repo.id, days_to_keep)
        
        return {
            "status_code": 200,
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name
            },
            "deleted_count": deleted_count,
            "days_kept": days_to_keep
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup commits: {e}")
        raise HTTPException(status_code=500, detail="커밋 히스토리 정리 실패")

def pr_generation_handler(commits: list[Commit]):
    """PR 생성 핸들러"""
    logging.info("Generating PR with %d commits", len(commits))
    return {
        "title": "Test PR",
        "body": "This is a test PR body",
    }
import requests
import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from .user_service import UserService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GitHubService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.github_uri = "https://api.github.com"
    
    def get_user_token(self, user_id: int) -> Optional[str]:
        """데이터베이스에서 사용자의 GitHub 토큰 조회"""
        user = self.user_service.get_user_by_id(user_id)

        logger.debug("Fetched user: %s", user)
        return user.github_access_token if user else None
    
    def _get_headers(self, token: str) -> Dict[str, str]:
        """GitHub API 헤더 생성"""
        return {
            "Authorization": f"Bearer {token}",
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    
    def get_user_repos(self, user_id: int) -> Dict:
        """사용자의 저장소 목록 조회"""
        token = self.get_user_token(user_id)
        if not token:
            logger.error(f"No token found for user {user_id}")
            raise ValueError("사용자의 GitHub 토큰을 찾을 수 없습니다.")
        
        path = "/user/repos"
        headers = self._get_headers(token)
        
        try:
            response = requests.get(
                self.github_uri + path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch repositories: {response.text}")
                raise ConnectionError(f"저장소 조회 실패: {response.status_code}")
            
            logger.info(f"Successfully fetched repositories for user {user_id}")
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ConnectionError(f"GitHub API 요청 실패: {e}")
    
    def get_commits(self, user_id: int, owner: str, repository_name: str) -> Dict:
        """저장소의 커밋 목록 조회"""
        token = self.get_user_token(user_id)
        if not token:
            logger.error(f"No token found for user {user_id}")
            raise ValueError("사용자의 GitHub 토큰을 찾을 수 없습니다.")
        
        path = f"/repos/{owner}/{repository_name}/commits"
        headers = self._get_headers(token)
        
        try:
            response = requests.get(
                self.github_uri + path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch commits: {response.text}")
                raise ConnectionError(f"커밋 조회 실패: {response.status_code}")
            
            logger.info(f"Successfully fetched commits for {owner}/{repository_name}")
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ConnectionError(f"GitHub API 요청 실패: {e}")
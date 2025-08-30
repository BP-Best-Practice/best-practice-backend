import requests
import logging
from datetime import datetime

from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from .user_service import UserService
from .repository_service import RepositoryService
from ..models import User, Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GitHubService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.repository_service = RepositoryService(db)
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
    
    def get_user_repos(self, user_id: int, force_refresh: bool = False) -> Dict:
        """사용자의 저장소 목록 조회 (ETag 캐싱 적용)"""
        
        # 1. 강제 새로고침이 아니면 캐시 체크
        if not force_refresh:
            cached_result = self._get_cached_repos(user_id)
            if cached_result:
                return cached_result
        
        # 2. GitHub API 호출 (ETag 활용)
        return self._fetch_repos_with_etag(user_id, force_refresh)
    
    def _get_cached_repos(self, user_id: int, max_age_hours: int = 1) -> Optional[Dict]:
        """캐시된 저장소 데이터 조회"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # 최근 동기화된 저장소가 있는지 확인
        recent_repo = self.db.query(Repository).filter(
            Repository.user_id == user_id,
            Repository.last_synced_at > cutoff_time
        ).first()
        
        if recent_repo:
            all_repos = self.repository_service.get_user_repositories(user_id)
            
            logger.info(f"Using cached repositories for user {user_id}")
            return {
                "status_code": 200,
                "data": [self._repo_to_dict(repo) for repo in all_repos],
                "source": "cache",
                "cached_at": recent_repo.last_synced_at.isoformat(),
                "cache_hit": True
            }
        
        return None
    
    def _fetch_repos_with_etag(self, user_id: int, force_refresh: bool = False) -> Dict:
        """ETag를 활용한 저장소 조회"""
        
        token = self.get_user_token(user_id)
        if not token:
            logger.error(f"No token found for user {user_id}")
            raise ValueError("사용자의 GitHub 토큰을 찾을 수 없습니다.")
        
        # ETag 조회
        user = self.user_service.get_user_by_id(user_id)
        stored_etag = None
        
        if user.preferences and not force_refresh:
            stored_etag = user.preferences.get('repos_etag')
        
        headers = self._get_headers(token)
        
        # If-None-Match 헤더 추가 (ETag가 있고 강제 새로고침이 아닌 경우)
        if stored_etag and not force_refresh:
            headers['If-None-Match'] = stored_etag
        
        try:
            logger.info(f"headers: {headers}")

            response = requests.get(
                f"{self.github_uri}/user/repos?sort=updated&per_page=100",
                headers=headers,
                timeout=10
            )

            logger.info(f"GitHub API response status: {response.status_code}")
            
            # 304 Not Modified - 변경사항 없음
            if response.status_code == 304:
                logger.info(f"No changes in repositories for user {user_id} (ETag match)")
                repos = self.repository_service.get_user_repositories(user_id)
                
                return {
                    "status_code": 304,
                    "data": [self._repo_to_dict(repo) for repo in repos],
                    "source": "etag_cache",
                    "etag_matched": True
                }
            
            # 200 OK - 변경사항 있음 또는 새로운 데이터
            if response.status_code == 200:
                logger.info(f"Response ETag: {response.headers.get('ETag')}")
                new_etag = response.headers.get('ETag')
                github_repos = response.json()
                
                # ETag 저장
                if new_etag:
                    self._store_etag(user_id, new_etag)
                
                # 저장소 동기화
                sync_result = self.repository_service.sync_repositories_incremental(
                    user_id, github_repos
                )
                
                sync_result['etag_updated'] = bool(new_etag)
                sync_result['new_etag'] = new_etag
                
                return sync_result
            
            # 다른 상태 코드 처리
            logger.error(f"Failed to fetch repositories: {response.status_code}")
            raise ConnectionError(f"저장소 조회 실패: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ConnectionError(f"GitHub API 요청 실패: {e}")
    
    def _store_etag(self, user_id: int, etag: str):
        """사용자의 ETag 저장"""
        user = self.user_service.get_user_by_id(user_id)
        if user:
            if not user.preferences:
                user.preferences = {}
            
            user.preferences['repos_etag'] = etag
            user.preferences['repos_etag_updated_at'] = datetime.now().isoformat()
            
            self.db.commit()
            logger.debug(f"Stored ETag for user {user_id}: {etag}")
    
    def _repo_to_dict(self, repo: Repository) -> Dict:
        """Repository 모델을 GitHub API 형식 딕셔너리로 변환"""
        return {
            "id": repo.github_repo_id,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": repo.is_private,
            "html_url": repo.html_url,
            "url": repo.url,
            "language": repo.language,
            "default_branch": repo.default_branch,
            "archived": repo.archived,
            "created_at": repo.repo_created_at.isoformat() if repo.repo_created_at else None,
            "updated_at": repo.repo_updated_at.isoformat() if repo.repo_updated_at else None,
            "pushed_at": repo.repo_pushed_at.isoformat() if repo.repo_pushed_at else None,
            # 추가 메타데이터
            "_db_id": repo.id,
            "_is_favorited": repo.is_favorited,
            "_access_count": repo.access_count,
            "_last_synced_at": repo.last_synced_at.isoformat() if repo.last_synced_at else None
        }
    
    def get_commits(self, user_id: int, owner: str, repository_name: str) -> Dict:
        """저장소의 커밋 목록 조회"""
        token = self.get_user_token(user_id)
        if not token:
            raise ValueError("사용자의 GitHub 토큰을 찾을 수 없습니다.")
        
        # 저장소 접근 횟수 증가
        repo = self.repository_service.get_repository_by_name(user_id, repository_name)
        if repo:
            self.repository_service.increment_access_count(repo.id)
        
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
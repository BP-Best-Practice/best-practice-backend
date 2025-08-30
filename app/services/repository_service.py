from sqlalchemy.orm import Session
from ..models import Repository, User
from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def sync_repositories_incremental(self, user_id: int, github_repos: List[Dict]) -> Dict:
        """증분 동기화: 변경된 저장소만 처리"""
        
        # 현재 DB의 저장소들을 GitHub ID로 매핑
        existing_repos = {
            repo.github_repo_id: repo 
            for repo in self.db.query(Repository).filter(Repository.user_id == user_id).all()
        }
        
        # GitHub에서 가져온 저장소들을 ID로 매핑
        github_repo_map = {repo['id']: repo for repo in github_repos}
        
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'unchanged': 0
        }
        
        # 새로운/업데이트된 저장소 처리
        for github_id, github_data in github_repo_map.items():
            if github_id in existing_repos:
                # 기존 저장소 업데이트 체크
                existing_repo = existing_repos[github_id]
                github_updated = self._parse_github_datetime(github_data.get('updated_at'))
                
                # 타임존 정규화 후 비교
                # 이전 코드: 타임존 정보가 있는 datetime(offset-aware)과 타임존 정보가 없는 datetime(offset-naive) 비교 에러 발생
                #   github_updated > existing_repo.repo_updated_at):
                # TypeError: can't compare offset-naive and offset-aware datetimes
                if github_updated and (not existing_repo.repo_updated_at or 
                                    self._normalize_datetime(github_updated) > self._normalize_datetime(existing_repo.repo_updated_at)):
                    self._update_repository_from_github_data(existing_repo, github_data)
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
            else:
                # 새 저장소 생성
                new_repo = self._create_repository_from_github_data(user_id, github_data)
                self.db.add(new_repo)
                stats['created'] += 1
        
        # 삭제된 저장소 처리 (아카이브 처리)
        for github_id, existing_repo in existing_repos.items():
            if github_id not in github_repo_map:
                existing_repo.archived = True
                stats['deleted'] += 1
        
        self.db.commit()
        logger.info(f"Repository sync stats for user {user_id}: {stats}")
        
        return {
            "status_code": 200,
            "data": github_repos,
            "sync_stats": stats,
            "source": "github_api"
        }
    
    def _create_repository_from_github_data(self, user_id: int, data: Dict) -> Repository:
        """GitHub 데이터로 새 Repository 객체 생성"""
        return Repository(
            github_repo_id=data['id'],
            user_id=user_id,
            name=data['name'],
            full_name=data['full_name'],
            description=data.get('description'),
            is_private=data.get('private', False),
            default_branch=data.get('default_branch', 'main'),
            language=data.get('language'),
            url=data.get('url', ''),
            html_url=data.get('html_url'),
            repo_created_at=self._parse_github_datetime(data.get('created_at')),
            repo_updated_at=self._parse_github_datetime(data.get('updated_at')),
            repo_pushed_at=self._parse_github_datetime(data.get('pushed_at')),
            archived=data.get('archived', False),
            last_synced_at=self._get_current_utc_datetime()
        )
    
    def _update_repository_from_github_data(self, repo: Repository, data: Dict):
        """기존 Repository 객체를 GitHub 데이터로 업데이트"""
        repo.name = data['name']
        repo.full_name = data['full_name']
        repo.description = data.get('description')
        repo.is_private = data.get('private', False)
        repo.default_branch = data.get('default_branch', 'main')
        repo.language = data.get('language')
        repo.url = data.get('url', repo.url)
        repo.html_url = data.get('html_url')
        repo.repo_updated_at = self._parse_github_datetime(data.get('updated_at'))
        repo.repo_pushed_at = self._parse_github_datetime(data.get('pushed_at'))
        repo.archived = data.get('archived', False)
        repo.last_synced_at = self._get_current_utc_datetime()
    
    def _parse_github_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """GitHub API의 ISO 형식 datetime 문자열을 파싱 (타임존 제거)"""
        if not datetime_str:
            return None
        try:
            # GitHub API는 UTC 시간을 'Z'로 표시
            if datetime_str.endswith('Z'):
                # Z를 제거하고 naive datetime으로 변환 (UTC 기준)
                dt = datetime.fromisoformat(datetime_str[:-1])
                return dt
            elif '+' in datetime_str or datetime_str.endswith('+00:00'):
                # 다른 타임존 형식 처리
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                # UTC로 변환 후 naive로 만들기
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            else:
                # 이미 naive datetime인 경우
                return datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse datetime '{datetime_str}': {e}")
            return None
    
    def _normalize_datetime(self, dt: Optional[datetime]) -> Optional[datetime]:
        """datetime을 비교 가능한 형태로 정규화 (모두 naive UTC로)"""
        if not dt:
            return None
        
        if dt.tzinfo is not None:
            # offset-aware인 경우 UTC로 변환 후 naive로 만들기
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            # 이미 naive인 경우 그대로 반환 (UTC라고 가정)
            return dt
    
    def _get_current_utc_datetime(self) -> datetime:
        """현재 UTC 시간을 naive datetime으로 반환"""
        return datetime.now(timezone.utc).replace(tzinfo=None)
    
    def get_user_repositories(self, user_id: int, include_archived: bool = False) -> List[Repository]:
        """사용자의 저장소 목록 조회"""
        query = self.db.query(Repository).filter(Repository.user_id == user_id)
        
        if not include_archived:
            query = query.filter(Repository.archived == False)
            
        return query.order_by(Repository.repo_pushed_at.desc()).all()
    
    def get_repository_by_name(self, user_id: int, repo_name: str) -> Optional[Repository]:
        """저장소명으로 조회"""
        return self.db.query(Repository).filter(
            Repository.user_id == user_id,
            Repository.name == repo_name,
            Repository.archived == False
        ).first()
    
    def increment_access_count(self, repository_id: int):
        """저장소 접근 횟수 증가"""
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if repo:
            repo.access_count += 1
            self.db.commit()
    
    def toggle_favorite(self, user_id: int, repository_id: int) -> bool:
        """저장소 즐겨찾기 토글"""
        repo = self.db.query(Repository).filter(
            Repository.id == repository_id,
            Repository.user_id == user_id
        ).first()
        
        if repo:
            repo.is_favorited = not repo.is_favorited
            self.db.commit()
            return repo.is_favorited
        return False
import logging

from sqlalchemy.orm import Session
from ..models import User, Repository
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_github_id(self, github_id: int) -> Optional[User]:
        """GitHub ID로 사용자 조회"""
        return self.db.query(User).filter(User.github_id == github_id).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """사용자 ID로 조회"""
        logger.debug(f"Fetching user with ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_or_update_user(self, github_user_data: dict) -> User:
        """GitHub 사용자 정보로 사용자 생성 또는 업데이트"""
        user = self.get_user_by_github_id(github_user_data['id'])
        
        if user:
            # 기존 사용자 업데이트
            user.username = github_user_data['login']
            user.email = github_user_data.get('email')
            user.display_name = github_user_data.get('name')
            user.avatar_url = github_user_data.get('avatar_url')
        else:
            # 새 사용자 생성
            user = User(
                github_id=github_user_data['id'],
                username=github_user_data['login'],
                email=github_user_data.get('email'),
                display_name=github_user_data.get('name'),
                avatar_url=github_user_data.get('avatar_url')
            )
            self.db.add(user)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user_token(self, user_id: int, access_token: str) -> Optional[User]:
        """사용자의 GitHub 액세스 토큰 업데이트"""
        user = self.get_user_by_id(user_id)
        if user:
            user.github_access_token = access_token
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_user_repositories(self, user_id: int) -> list[Repository]:
        """사용자의 저장소 목록 조회"""
        return self.db.query(Repository).filter(Repository.user_id == user_id).all()

"""커밋 히스토리 관리 서비스"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from sqlalchemy.orm import Session
from sqlalchemy.sql import functions as func
from sqlalchemy import and_, desc
from app.models import CommitHistory

logger = logging.getLogger(__name__)

class CommitHistoryService:
    """커밋 히스토리 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_commit_history(self, commit_info: Dict) -> Optional[CommitHistory]:
        """커밋 히스토리 저장 또는 업데이트"""
        try:
            # 기존 커밋 히스토리 확인
            existing_commit = self.db.query(CommitHistory).filter(
                and_(
                    CommitHistory.repository_id == commit_info['repository_id'],
                    CommitHistory.commit_sha == commit_info['commit_sha']
                )
            ).first()
            
            if existing_commit:
                # 기존 데이터 업데이트
                for key, value in commit_info.items():
                    if hasattr(existing_commit, key):
                        setattr(existing_commit, key, value)
                existing_commit.cached_at = datetime.now()
                
                self.db.commit()
                logger.debug(f"Updated commit history: {commit_info['commit_sha']}")
                return existing_commit
            else:
                # 새로운 커밋 히스토리 생성
                commit_history = CommitHistory(**commit_info)
                self.db.add(commit_history)
                self.db.commit()
                self.db.refresh(commit_history)
                
                logger.debug(f"Saved new commit history: {commit_info['commit_sha']}")
                return commit_history
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save commit history: {e}")
            return None
    
    def get_commit_by_sha(self, repository_id: int, commit_sha: str) -> Optional[CommitHistory]:
        """SHA로 커밋 히스토리 조회"""
        return self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.commit_sha == commit_sha
            )
        ).first()
    
    def get_cached_commits(self, repository_id: int, max_age_minutes: int = 30, 
                          limit: int = 100) -> List[CommitHistory]:
        """캐시된 커밋 히스토리 목록 조회"""
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        return self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.cached_at > cutoff_time
            )
        ).order_by(desc(CommitHistory.committed_at)).limit(limit).all()
    
    def get_repository_commits(self, repository_id: int, limit: int = 100) -> List[CommitHistory]:
        """저장소의 모든 커밋 히스토리 조회"""
        return self.db.query(CommitHistory).filter(
            CommitHistory.repository_id == repository_id
        ).order_by(desc(CommitHistory.committed_at)).limit(limit).all()
    
    def get_commits_by_author(self, repository_id: int, author_email: str, 
                             limit: int = 50) -> List[CommitHistory]:
        """특정 작성자의 커밋 히스토리 조회"""
        return self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.author_email == author_email
            )
        ).order_by(desc(CommitHistory.committed_at)).limit(limit).all()
    
    def get_commits_by_date_range(self, repository_id: int, start_date: datetime, 
                                 end_date: datetime) -> List[CommitHistory]:
        """날짜 범위로 커밋 히스토리 조회"""
        return self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.committed_at >= start_date,
                CommitHistory.committed_at <= end_date
            )
        ).order_by(desc(CommitHistory.committed_at)).all()
    
    def get_commits_stats(self, repository_id: int) -> Dict:
        """저장소 커밋 통계"""
        
        stats = self.db.query(
            func.count(CommitHistory.id).label('total_commits'),
            func.sum(CommitHistory.additions).label('total_additions'),
            func.sum(CommitHistory.deletions).label('total_deletions'),
            func.sum(CommitHistory.file_count).label('total_files_changed'),
            #func.count(func.distinct(CommitHistory.author_email)).label('unique_authors')
        ).filter(CommitHistory.repository_id == repository_id).first()
        
        return {
            'total_commits': stats.total_commits or 0,
            'total_additions': stats.total_additions or 0,
            'total_deletions': stats.total_deletions or 0,
            'total_files_changed': stats.total_files_changed or 0,
            'unique_authors': stats.unique_authors or 0
        }
    
    def cleanup_old_commits(self, repository_id: int, days_to_keep: int = 30) -> int:
        """오래된 커밋 히스토리 정리"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.cached_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old commit histories for repository {repository_id}")
        
        return deleted_count
    
    def get_recent_activity(self, repository_id: int, days: int = 7) -> List[Dict]:
        """최근 활동 요약"""
        start_date = datetime.now() - timedelta(days=days)
        
        commits = self.db.query(CommitHistory).filter(
            and_(
                CommitHistory.repository_id == repository_id,
                CommitHistory.committed_at >= start_date
            )
        ).order_by(desc(CommitHistory.committed_at)).all()
        
        activity = []
        for commit in commits:
            activity.append({
                'sha': commit.commit_sha,
                'message': commit.commit_message,
                'author': commit.author_name,
                'committed_at': commit.committed_at,
                'additions': commit.additions or 0,
                'deletions': commit.deletions or 0,
                'file_count': commit.file_count or 0
            })
        
        return activity
    
    def batch_save_commits(self, commits_data: List[Dict]) -> Dict:
        """대량 커밋 데이터 저장"""
        saved_count = 0
        updated_count = 0
        failed_count = 0
        
        for commit_info in commits_data:
            try:
                existing_commit = self.db.query(CommitHistory).filter(
                    and_(
                        CommitHistory.repository_id == commit_info['repository_id'],
                        CommitHistory.commit_sha == commit_info['commit_sha']
                    )
                ).first()
                
                if existing_commit:
                    # 업데이트
                    for key, value in commit_info.items():
                        if hasattr(existing_commit, key):
                            setattr(existing_commit, key, value)
                    existing_commit.cached_at = datetime.now()
                    updated_count += 1
                else:
                    # 새로 저장
                    commit_history = CommitHistory(**commit_info)
                    self.db.add(commit_history)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to save commit {commit_info.get('commit_sha')}: {e}")
                failed_count += 1
        
        try:
            self.db.commit()
            logger.info(f"Batch save completed: {saved_count} saved, {updated_count} updated, {failed_count} failed")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Batch save failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        return {
            'success': True,
            'saved_count': saved_count,
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_processed': len(commits_data)
        }
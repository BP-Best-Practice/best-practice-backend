from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, BIGINT, ARRAY, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .database import Base

class User(Base):
    __tablename__ = "user_account"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    github_id = Column(BIGINT, unique=True, nullable=False)
    github_access_token = Column(Text, nullable=False)
    username = Column(String(255), nullable=False)
    email = Column(String(255))
    
    # Profile fields
    display_name = Column(String(255))
    avatar_url = Column(Text)
    subscription_type = Column(String(50), default='FREE')
    monthly_usage_count = Column(Integer, default=0)
    preferences = Column(JSON)
    
    # Meta fields
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP)
    
    # Relationships
    repositories = relationship("Repository", back_populates="user", cascade="all, delete-orphan")
    pr_generations = relationship("PRGeneration", back_populates="user", cascade="all, delete-orphan")
    pr_templates = relationship("PRTemplate", back_populates="user", cascade="all, delete-orphan")

class Repository(Base):
    __tablename__ = "repository"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    github_repo_id = Column(BIGINT, unique=True, nullable=False)
    user_id = Column(BIGINT, ForeignKey("user_account.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), nullable=False)
    description = Column(Text)
    is_private = Column(Boolean, default=False)
    default_branch = Column(String(100), default='main')
    language = Column(String(100))

    url = Column(Text, nullable=False)
    html_url = Column(Text, nullable=True)
    repo_created_at = Column(TIMESTAMP)
    repo_updated_at = Column(TIMESTAMP)
    repo_pushed_at = Column(TIMESTAMP)
    
    archived = Column(Boolean, default=False)
    is_favorited = Column(Boolean, default=False)
    access_count = Column(Integer, default=0)
    last_synced_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="repositories")
    pr_generations = relationship("PRGeneration", back_populates="repository", cascade="all, delete-orphan")
    commit_histories = relationship("CommitHistory", back_populates="repository", cascade="all, delete-orphan")

class PRGeneration(Base):
    __tablename__ = "pr_generation"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("user_account.id", ondelete="CASCADE"))
    repository_id = Column(BIGINT, ForeignKey("repository.id", ondelete="CASCADE"))
    session_id = Column(String(255), nullable=False)
    commit_shas = Column(ARRAY(Text), nullable=False)
    generated_title = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    user_feedback_rating = Column(Integer)
    user_feedback_comment = Column(Text)
    style_preference = Column(String(50))
    template_used = Column(String(100))
    ai_model_version = Column(String(50))
    processing_time_ms = Column(Integer)
    token_usage = Column(Integer)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pr_generations")
    repository = relationship("Repository", back_populates="pr_generations")

class CommitHistory(Base):
    __tablename__ = "commit_history"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    repository_id = Column(BIGINT, ForeignKey("repository.id", ondelete="CASCADE"))
    commit_sha = Column(String(40), nullable=False)
    commit_message = Column(Text, nullable=False)
    author_name = Column(String(255))
    author_email = Column(String(255))
    committed_at = Column(TIMESTAMP, nullable=False)
    files_changed = Column(JSON)
    file_count = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    cached_at = Column(TIMESTAMP, default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="commit_histories")

class PRTemplate(Base):
    __tablename__ = "pr_template"
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("user_account.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    title_template = Column(Text, nullable=False)
    content_template = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pr_templates")
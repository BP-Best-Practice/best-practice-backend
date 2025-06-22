# 🤖 AI PR Message Generator

> GitHub 커밋 히스토리를 기반으로 AI가 자동으로 Pull Request 제목과 내용을 추천해주는 웹 서비스

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Test Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)
![TDD](https://img.shields.io/badge/Development-TDD-red.svg)

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [아키텍처](#-아키텍처)
- [TDD 개발 방식](#-tdd-개발-방식)
- [설치 및 실행](#-설치-및-실행)
- [API 문서](#-api-문서)
- [테스트](#-테스트)
- [데이터베이스 설계](#-데이터베이스-설계)
- [기여하기](#-기여하기)

## 🎯 프로젝트 소개

### 해결하고자 하는 문제
- 매번 PR 제목과 설명을 작성하는데 소요되는 시간과 노력
- 일관성 없는 PR 메시지로 인한 코드 리뷰 효율성 저하
- 신입 개발자들의 적절한 PR 작성 방법에 대한 어려움

### 목표
- ⏰ 개발자들의 PR 작성 시간을 **50% 단축**
- 📝 일관성 있고 명확한 PR 메시지 생성
- 🔄 코드 리뷰 프로세스 개선

### 타겟 사용자
- **개인 개발자**: 사이드 프로젝트나 개인 레포지토리 관리
- **스타트업/중소기업 개발자**: 빠른 개발 속도가 중요한 환경
- **오픈소스 기여자**: 다양한 프로젝트에 기여하는 개발자
- **신입 개발자**: PR 작성 방법을 배우고 싶은 주니어 개발자

## ✨ 주요 기능

### MVP 기능
- 🔐 **GitHub OAuth 연동**: 안전한 GitHub 계정 인증
- 📂 **레포지토리 관리**: 사용자 레포지토리 목록 조회 및 선택
- 📋 **커밋 선택**: 체크박스 형태의 직관적인 커밋 선택 UI
- 🤖 **AI 기반 PR 생성**: OpenAI GPT를 활용한 지능적인 PR 메시지 생성
- 📊 **변경사항 분석**: 파일 변경 타입 및 복잡도 분석

### 확장 기능 (Post-MVP)
- 🎨 **스타일 커스터마이징**: 톤앤매너 선택 (간결함/상세함/기술적)
- 📑 **팀 템플릿 지원**: 팀별 PR 템플릿 및 컨벤션 적용
- 🧠 **개인화 학습**: 사용자 선호 스타일 학습 및 적용
- 👥 **리뷰어 추천**: 코드 변경사항 기반 적절한 리뷰어 제안

## 🛠 기술 스택

### Backend
- 🐍 **Python 3.11+**: 메인 개발 언어
- ⚡ **FastAPI**: 고성능 비동기 웹 프레임워크
- 🗄️ **PostgreSQL**: 메인 데이터베이스
- 🔄 **SQLAlchemy 2.0**: ORM (async 지원)
- 🧪 **pytest**: 테스트 프레임워크
- 📊 **Pydantic**: 데이터 검증 및 시리얼라이제이션

### External APIs
- 🐙 **GitHub REST API**: 레포지토리 및 커밋 데이터 연동
- 🤖 **OpenAI GPT API**: AI 기반 PR 메시지 생성
- 🔐 **GitHub OAuth 2.0**: 사용자 인증

### DevOps & Tools
- 🐳 **Docker**: 컨테이너화
- 🧹 **Black**: 코드 포매팅
- 📏 **Flake8**: 코드 린팅
- 📈 **Coverage.py**: 테스트 커버리지 측정

## 🏗 아키텍처

### Clean Architecture 적용
```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                   (FastAPI Routes)                         │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                         │
│                   (Use Cases)                              │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                             │
│              (Entities, Repositories)                      │
├─────────────────────────────────────────────────────────────┤
│                Infrastructure Layer                         │
│        (Database, External APIs, Services)                 │
└─────────────────────────────────────────────────────────────┘
```

### 디렉토리 구조
```
src/
├── domain/
│   ├── entities/          # 도메인 엔티티
│   ├── repositories/      # 레포지토리 인터페이스
│   └── services/          # 도메인 서비스
├── application/
│   ├── use_cases/         # 유스케이스
│   └── dtos/              # 데이터 전송 객체
├── infrastructure/
│   ├── database/          # 데이터베이스 구현
│   ├── external/          # 외부 API 클라이언트
│   └── repositories/      # 레포지토리 구현
└── presentation/
    ├── api/               # FastAPI 라우터
    ├── schemas/           # Pydantic 스키마
    └── dependencies/      # 의존성 주입
```

## 🧪 TDD 개발 방식

이 프로젝트는 **Test-Driven Development (TDD)** 방식으로 개발되고 있습니다.

### TDD 사이클 적용
```
🔴 Red → 🟢 Green → 🔵 Refactor
```

1. **🔴 Red**: 실패하는 테스트 작성
2. **🟢 Green**: 테스트를 통과하는 최소한의 코드 작성
3. **🔵 Refactor**: 코드 품질 개선 및 리팩토링

### 테스트 전략
- **Unit Tests**: 각 컴포넌트의 개별 기능 테스트
- **Integration Tests**: 외부 API 및 데이터베이스 연동 테스트
- **End-to-End Tests**: 전체 사용자 플로우 테스트

### 테스트 커버리지 목표
- 🎯 **목표 커버리지**: 95% 이상
- 📊 **현재 커버리지**: ![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)

### TDD 개발 예시
```python
# 1. 🔴 Red: 실패하는 테스트 작성
def test_generate_pr_title_from_commits():
    # Given
    commits = [
        Commit(message="Add user authentication", files_changed=5),
        Commit(message="Fix login validation", files_changed=2)
    ]
    
    # When
    result = pr_generator.generate_title(commits)
    
    # Then
    assert "feat: implement user authentication" in result.lower()

# 2. 🟢 Green: 테스트를 통과하는 코드 작성
class PRGenerator:
    def generate_title(self, commits: List[Commit]) -> str:
        # 최소한의 구현으로 테스트 통과
        return "feat: implement user authentication"

# 3. 🔵 Refactor: 실제 AI 연동 및 로직 개선
class PRGenerator:
    def generate_title(self, commits: List[Commit]) -> str:
        commit_messages = [commit.message for commit in commits]
        return self.ai_service.generate_title(commit_messages)
```

## 🚀 설치 및 실행

### 사전 요구사항
- Python 3.11+
- PostgreSQL 15+
- Docker (선택사항)

### 로컬 개발 환경 설정

1. **프로젝트 클론**
```bash
git clone https://github.com/your-username/pr-generation-service.git
cd pr-generation-service
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 의존성
```

4. **환경변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정
```

5. **데이터베이스 설정**
```bash
# 데이터베이스 생성
createdb pr_generation_db

# 마이그레이션 실행
alembic upgrade head
```

6. **개발 서버 실행**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker를 사용한 실행

```bash
# 개발 환경
docker-compose -f docker-compose.dev.yml up

# 프로덕션 환경
docker-compose up
```

## 📚 API 문서

### 자동 생성된 API 문서
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/github` | GitHub OAuth 인증 |
| GET | `/users/me` | 현재 사용자 정보 조회 |
| GET | `/repositories` | 사용자 레포지토리 목록 |
| GET | `/repositories/{repo_id}/commits` | 레포지토리 커밋 목록 |
| POST | `/pr/generate` | PR 메시지 생성 |
| GET | `/pr/history` | PR 생성 히스토리 |

### API 사용 예시

```python
# PR 메시지 생성 요청
POST /pr/generate
{
    "repository_id": 123,
    "commit_ids": ["abc123", "def456", "ghi789"],
    "style": "detailed",
    "template_id": null
}

# 응답
{
    "title": "feat: implement user authentication system",
    "description": "## Changes\n- Add JWT-based authentication\n- Implement password hashing\n- Add user login/logout endpoints\n\n## Testing\n- All authentication flows tested\n- Unit tests added for security functions",
    "generated_at": "2024-06-22T10:30:00Z",
    "commit_count": 3
}
```

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=src --cov-report=html

# 특정 테스트 파일 실행
pytest tests/test_pr_generator.py

# 마커별 테스트 실행
pytest -m "unit"           # 단위 테스트만
pytest -m "integration"    # 통합 테스트만
pytest -m "e2e"           # E2E 테스트만
```

### 테스트 작성 가이드

```python
# 단위 테스트 예시
@pytest.mark.unit
class TestPRGenerator:
    def test_generate_title_with_single_commit(self):
        # Given
        commits = [Commit(message="Add user login", type="feat")]
        
        # When
        result = pr_generator.generate_title(commits)
        
        # Then
        assert result.startswith("feat:")
        assert "login" in result.lower()

# 통합 테스트 예시
@pytest.mark.integration
class TestGitHubIntegration:
    async def test_fetch_repository_commits(self, github_client):
        # Given
        repo_id = "test-repo"
        
        # When
        commits = await github_client.get_commits(repo_id)
        
        # Then
        assert len(commits) > 0
        assert all(commit.sha for commit in commits)
```

## 🗄 데이터베이스 설계

### ERD (Entity Relationship Diagram)
전체 데이터베이스 설계는 다음 링크에서 확인할 수 있습니다:

**🔗 [ERD 다이어그램 보기](https://dbdiagram.io/d/PR-generation-service-ERD-68527617f039ec6d36c0137c)**

### 주요 테이블 구조

#### Users
- 사용자 정보 및 GitHub 연동 데이터
- OAuth 토큰 및 사용자 설정 관리

#### Repositories
- 연동된 GitHub 레포지토리 정보
- 접근 권한 및 동기화 상태 관리

#### Commits
- 가져온 커밋 정보 캐싱
- 변경사항 메타데이터 저장

#### PR_Generations
- 생성된 PR 메시지 히스토리
- 사용자 피드백 및 개선 데이터

#### User_Preferences
- 사용자별 스타일 설정
- 개인화된 템플릿 관리

### 마이그레이션 관리

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "Add user preferences table"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 🤝 기여하기

### 개발 프로세스

1. **이슈 생성**: 새로운 기능이나 버그를 이슈로 등록
2. **브랜치 생성**: `feature/issue-number` 또는 `bugfix/issue-number`
3. **TDD 사이클**: Red → Green → Refactor 사이클 적용
4. **테스트 작성**: 새로운 코드에 대한 테스트 필수 작성
5. **코드 리뷰**: PR 생성 후 리뷰 진행
6. **머지**: 승인 후 메인 브랜치에 머지

### 코드 스타일 가이드

```bash
# 코드 포매팅
black src tests

# 린팅 실행
flake8 src tests

# 타입 체킹
mypy src
```

### 커밋 메시지 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포매팅 변경
refactor: 코드 리팩토링
test: 테스트 코드 추가/수정
chore: 빌드 과정 또는 보조 도구 변경
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙋‍♂️ 문의 및 지원

- 📧 이메일: your-email@example.com
- 🐛 버그 리포트: [GitHub Issues](https://github.com/your-username/pr-generation-service/issues)
- 💡 기능 제안: [GitHub Discussions](https://github.com/your-username/pr-generation-service/discussions)

---

<div align="center">
  <sub>Built with ❤️ using TDD principles</sub>
</div>
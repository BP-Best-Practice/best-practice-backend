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
- [데이터베이스 설계](#-데이터베이스-설계)

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
- 📈 **Coverage.py**: 테스트 커버리지 측정

## 🏗 아키텍처


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

## 🗄 데이터베이스 설계

### ERD (Entity Relationship Diagram)
전체 데이터베이스 설계는 다음 링크에서 확인할 수 있습니다:

**🔗 [ERD 다이어그램 보기](https://dbdiagram.io/d/PR-generation-service-ERD-68527617f039ec6d36c0137c)**

### 주요 테이블 구조

#### user
- 사용자 정보 및 GitHub 연동 데이터
- OAuth 토큰 및 사용자 설정 관리

#### repository
- 연동된 GitHub 레포지토리 정보
- 접근 권한 및 동기화 상태 관리

#### commit_history
- 가져온 커밋 정보 캐싱
- 변경사항 메타데이터 저장

#### pr_generation
- 생성된 PR 메시지 히스토리
- 사용자 피드백 및 개선 데이터

#### pr_template
- 사용자별 스타일 설정
- 개인화된 템플릿 관리
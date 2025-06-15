# MOVIECHAT

## 프로젝트 소개

MOVIECHAT은 사용자와의 대화를 통해 영화 취향을 분석하고, 이에 기반한 영화를 추천하거나 영화 관련 토론을 나눌수 있는 LLM 기반 영화 대화 서비스입니다.

기존의 별점 기반 추천 시스템을 넘어, 자연어 대화를 통해 사용자의 선호도를 더 깊이 이해하며, 북마크/좋아요/싫어요와 같은 기능을 통해 피드백을 반영한 맞춤형 추천을 제공합니다.

## 주요 기능

### 영화 추천/토론

- 사용자와의 대화를 통해 취향을 파악하고, 적절한 영화를 추천하거나 토론하는 등 영화와 관련된 심도있는 이야기를 나눌 수 있습니다.

### 몰입형 대화

- 영화 속 등장인물과 직접 대화하며 영화 내용을 토론하는 등 더욱더 영화에 몰입할 수 있습니다.

### 북마크/아카이빙

- 사용자가 남긴 좋아요/싫어요/북마크 정보를 바탕으로 개인화된 영화 추천을 진행합니다.
- 이 정보는 사용자의 영화 취향으로 반영되어 더욱더 개인화된 맞춤 영화 비서로서 역할을 강화합니다.

## 기술 스택

- Frontend: React
- Backend: FastAPI, Langchain
- Database: SQLite, ChromaDB

## 팀원 소개

| 이름   | 역할                 | GitHub                                       |
| ------ | -------------------- | -------------------------------------------- |
| 강병희 | 프론트엔드           | [@byungKHee](https://github.com/byungKHee)   |
| 박진우 | 프론트엔드           | [@EddieDawn](https://github.com/EddieDawn)   |
| 박찬원 | 백엔드, 데이터베이스 | [@softkau](https://github.com/softkau)       |
| 이해민 | LLM                  | [@zhaemin](https://github.com/zhaemin)       |
| 이상훈 | LLM                  | [@lsh-Brecht](https://github.com/lsh-Brecht) |

## 프로젝트 실행 방법

### 백엔드

```bash
# backend 폴더로 이동
cd backend

# Python 가상환경 생성 및 활성화 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# src 폴더로 이동하여 서버 실행
cd src
uvicorn main:app --reload
```

### 프론트엔드

```bash
# frontend 폴더로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

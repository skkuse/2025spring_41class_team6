from typing import Optional, List, cast
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from common.env import ENV_BACKEND_ROOT
from datetime import datetime
from rapidfuzz import fuzz
from common.logging_config import logger

def best_title_match(results, query_title):
    best_doc = None
    best_score = 0

    for doc in results:
        candidate_title = doc.metadata.get("title", "")
        score = fuzz.token_sort_ratio(query_title, candidate_title)
        if score > best_score:
            best_score = score
            best_doc = doc

    return best_doc if best_score > 65 else None  # threshold

# GPT === "신"
__all__ = ["MovieMeta", "chroma_fuzzy_search", "chroma_insert", "chroma_delete", "chroma_update"]

# 전역 경로 (환경 변수)
CHROMA_DB_PATH = cast(str, ENV_BACKEND_ROOT) + '/src/database/chroma'
embedding_model = OpenAIEmbeddings()

# 🎬 영화 메타데이터 Pydantic 모델
class MovieMeta(BaseModel):
    sqlite_id: int              # Movie.id 값
    tmdb_id: Optional[int]      # Duplicated Data. 정합성 체크용
    title: str                  # 영화 제목 (TMDB 기준)
    series: int
    year: Optional[int]         # 영화 출시일
    created_at: str             # 문서 생성일 (너무 오래된 거면 업데이트)

# 📦 Chroma DB 세션 반환
def _chroma_get():
    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)

# Chroma Query 생성
def _build_query(title: str, keywords: Optional[dict] = None) -> str:
    parts = [f"영화 제목: {title}"]
    others = []
    if keywords:
        for k, v in keywords.items():
            match k:
                case _:
                    others.append(str(v))
        others = "관련 키워드: " + ', '.join(others)
    return " | ".join(parts)

# 🔍 fuzzy 검색 (유사 문장 기반 검색)
def chroma_fuzzy_search(title: str, keywords: Optional[dict] = None) -> Optional[MovieMeta]:
    db = _chroma_get()
    query = _build_query(title, keywords)
    logger.info(f"FUZZY search 쿼리: {query}")
    
    try:
        f = { "filter": {
                "year": {
                  "$gte": keywords["year"] - 1,
                  "$lte": keywords["year"] + 1
                }
        }} if keywords and keywords.get("year") else None
        f = None
        results = db.similarity_search(query, k=10)
    except Exception as e:
        print(f"[Chroma Error] {e}")
        return None

    best_doc = best_title_match(results, title)
    if not best_doc:
        return None

    meta = best_doc.metadata
    if meta.get("sqlite_id"):
        return MovieMeta(
            sqlite_id=meta["sqlite_id"],
            tmdb_id=meta.get("tmdb_id"),
            series=meta.get("series"),
            title=meta.get("title", title),
            year=meta.get("year"),
            created_at=meta.get("created_at")
        )

# ➕ 삽입 (SQLite 정보 기반으로 Chroma에 삽입)
def chroma_insert(meta: MovieMeta):
    db = _chroma_get()
    metadata = meta.model_dump()
    
    content = (
        f"영화 제목: {meta.title}\n"
        f"개봉년도: {meta.year}\n"
        f"시리즈: {meta.series}\n"
        f"SQLite ID: {meta.sqlite_id}\n"
        f"TMDB ID: {meta.tmdb_id}"
    )
    logger.info(f"크로마 DB에 삽입 중... {content}")

    # metadata와 자연어 기반 content를 동시에 저장
    doc = Document(page_content=content, metadata=metadata)
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents([doc])
    db.add_documents(chunks)

def chroma_delete(meta: MovieMeta):
    logger.info(f"삭제중 {meta}")
    db = _chroma_get()
    try:
        # sqlite_id를 유일 key로 사용
        db.delete([meta.sqlite_id])
    except Exception:
        print("[Chroma Error] 영화 삭제 중 오류 발생")

# 🔁 업데이트 (기존 삭제 후 재삽입)
def chroma_update(meta: MovieMeta):
    db = _chroma_get()
    try:
        # sqlite_id를 유일 key로 사용
        db.delete([meta.sqlite_id])
    except Exception:
        print("[Chroma Error] 영화 업데이트 중 오류 발생")

    chroma_insert(meta)

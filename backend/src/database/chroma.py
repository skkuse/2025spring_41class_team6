"""
MovieChat 로컬 DB의 영화 title fuzzy matching에 사용되는 chroma DB입니다.
"""

from typing import Optional, List, cast
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from common.env import ENV_BACKEND_ROOT
from datetime import datetime

__all__ = ["MovieMeta", "chroma_fuzzy_search", "chroma_insert", "chroma_delete"]

# 전역 경로 (환경 변수)
CHROMA_DB_PATH = cast(str, ENV_BACKEND_ROOT) + '/src/database/chroma'
embedding_model = OpenAIEmbeddings()

# 영화 메타데이터 Pydantic 모델
class MovieMeta(BaseModel):
    sqlite_id: int              # Movie.id 값
    tmdb_id: Optional[int]      # Duplicated Data. 정합성 체크용
    title: str                  # 영화 제목 (TMDB 기준)
    release_date: Optional[str] # 영화 출시일
    genres: Optional[List[str]] # 장르
    created_at: str             # 문서 생성일 (너무 오래된 거면 업데이트)

# Chroma DB 세션 반환
def _chroma_get():
    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)

# Chroma Query 생성
def _build_query(title: str, keywords: Optional[List[str]] = None) -> str:
    parts = [f"영화 제목: {title}"]
    if keywords:
        parts.append(f"관련 키워드: {', '.join(keywords)}")
    # query := "영화 제목: {제목} | 관련 키워드: keyword0, keyword1, keyword2 ..."
    return " | ".join(parts)

def chroma_fuzzy_search(title: str, keywords: Optional[List[str]] = None) -> Optional[MovieMeta]:
    """
    Chroma DB를 활용하여 title과 keyword로 유사한 영화 제목을 찾습니다.  
    Sqlite DB의 Movie Entry를 Fuzzy search하기 위해 사용됩니다.

    Args:
      title:
        찾고자 하는 영화 제목
      keywords:
        찾고자 하는 영화와 관련된 키워드
    Returns:
      MovieMeta:
        유사하다고 판단된 영화의 metadata  
    """
    db = _chroma_get()
    query = _build_query(title, keywords)
    
    try:
        results = db.similarity_search(query, k=10)
    except Exception as e:
        print(f"[Chroma Error] {e}")
        return None

    if not results:
        return None

    for doc in results:
        meta = doc.metadata
        if meta.get("sqlite_id"):
            return MovieMeta(
                sqlite_id=meta["sqlite_id"],
                tmdb_id=meta.get("tmdb_id"),
                title=meta.get("title", title),
                release_date=meta.get("release_date"),
                genres=meta.get("genres"),
                created_at=meta.get("created_at")
            )
    return None

def chroma_insert(meta: MovieMeta):
    """
    Chroma DB에 영화 metadata를 등록합니다.  
    """
    db = _chroma_get()
    metadata = meta.model_dump()
    
    content = (
        f"[영화 제목] {meta.title}\n"
        f"[출시일] {meta.release_date}\n"
        f"[장르] {', '.join(meta.genres or [])}\n"
        f"[SQLite ID] {meta.sqlite_id}\n"
        f"[TMDB ID] {meta.tmdb_id}"
    )

    # metadata와 자연어 기반 content를 동시에 저장
    doc = Document(page_content=content, metadata=metadata)
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents([doc])
    db.add_documents(chunks)

def chroma_delete(meta: MovieMeta):
    """
    Chroma DB에 영화 metadata를 삭제합니다.  
    """
    db = _chroma_get()
    try:
        # sqlite_id를 유일 key로 사용
        db.delete([meta.sqlite_id])
    except Exception:
        print("[Chroma Error] 영화 삭제 중 오류 발생")

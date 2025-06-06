import llm.qachat as qachat
import llm.crawler as crawler
from database.utils import *
import json
from langchain.schema import messages_to_dict, messages_from_dict
from typing import TypedDict

from database.chroma import *
from datetime import datetime, timezone


class SummaryType(TypedDict):
    """
    대화방의 대화 내역의 필요한 정보를 담고 있는 opaque type
    """
    summary: str
    messages: list[dict]

def get_summary_from_qachat(room_id: int) -> SummaryType:
    memory = qachat.get_memory(str(room_id))
    summary = memory.moving_summary_buffer
    messages = memory.chat_memory.messages
    messages_dict = messages_to_dict(messages)
    return { "summary": summary, "messages": messages_dict }

def _preprocess_user_input(user_input: str) -> str:
    return user_input

async def send_message_to_qachat(db: Session, user_id: int, room_id: int, message: str):
    """
    message를 AI agent에게 전송하고, 그 응답을 하나의 string으로 반환합니다.  
    비동기 함수이기 때문에 응답을 받을 때는 `await`를 사용해주세요.
    """
    full_answer = ""
    movie_ids = []
    
    async for content in stream_send_message_to_qachat(db, user_id, room_id, message):
        v = content.get("content")
        t = content.get("type")
        if t == "message":
            full_answer += v if v else ""
        elif t == "recommendation":
            movie_ids = v

    return { "message": full_answer, "recommendation": movie_ids }

def fuzzy_search(db: Session, title: str, keyword: str|None):
    print(f"[FUZZY]\nTITLE: {title}\nKEYWORD: {keyword}\n에 대한 로컬 DB 검색 중...")
    meta = chroma_fuzzy_search(title, [keyword] if keyword else None)
    if meta:
        movie = db_find_movie_by_id(db, meta.sqlite_id, True)
        if not movie:
            if meta.tmdb_id is not None:
                movie = update_movie_by_tmdb_id(db, meta.tmdb_id)
            else:
                movies = update_movie_by_tmdb_search(db, search={
                    "query": meta.title,
                    "primary_release_year": meta.release_date or "",
                })
                if len(movies) > 0:
                    movie = movies[0]

            if movie:
                chroma_delete(meta)
                meta.sqlite_id = movie.id
                meta.tmdb_id = movie.tmdb_id
                meta.genres = meta.genres
                meta.created_at = datetime.now(timezone.utc).isoformat()
                meta.title = movie.title
                if movie.release_date:
                    meta.release_date = movie.release_date.isoformat()
                chroma_insert(meta)
            else:
                chroma_delete(meta)
                return
    else:
        movies = update_movie_by_tmdb_search(db, search={
            "query": title,
            "primary_release_year": keyword or ""
        })
        if len(movies) == 0:
            return

        movie = movies[0]
    
    print(f"[FUZZY] 검색 성공")
    return movie


def stream_send_message_to_qachat(db: Session, user_id: int, room_id: int, message: str):
    """
    message를 AI agent에게 전송하고, 그 응답을 stream 모드로 반환하는 AsyncGenerator를 반환합니다
    """
    message = _preprocess_user_input(message)
    titles: list[str] = []
    hints = qachat.extract_titles_and_metadata_with_llm(message)
    for hint in hints:
        title = hint.get("title")
        keyword = hint.get("keyword")
        assert(title)

        if qachat.is_cached_on_chroma(title):
            continue

        movie = fuzzy_search(db, title, keyword)
        if movie is None:
            continue
        
        print(f"[send_message_to_qachat] db_data:\n{movie}\n\n")
        
        # 4. See if we have any outdated, or missing data in our DB
        if not movie.wiki_document:
            movie.wiki_document = crawler.get_wikipedia_content(title)
            if movie.wiki_document:
                db_update_wikipedia_data(db, movie.id, movie.wiki_document)

        # 5. 영화 리뷰를 불러옵니다. 3번째 인자를 None이 아닌 것으로 설정하면 그 수만큼만 리뷰를 불러옵니다
        reviews = db_get_movie_reviews(db, movie.id, None)
        if not reviews:
            print(f"{title}에 대한 리뷰가 DB에 없습니다. 리뷰를 크롤링 합니다...")
            reviews = cast(list[str], crawler.get_watcha_reviews(title))
            db_add_movie_reviews(db, movie.id, reviews)

        # 6. Let's cache it
        qachat.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, reviews)
        print(f"[send_message_to_qachat] chroma에 {title}(이)가 캐시되었습니다")

    if not hints:
        print(f"[send_message_to_qachat] 감지된 영화 없음")
    
    # 채팅방 ID를 session ID로 사용합니다.
    session_id = str(room_id)

    if not qachat.is_memory_on_cache(session_id):
        print(f"[send_message_to_qachat] session cache가 비어있습니다")
        context = db_get_chatroom_context(db, room_id).summary
        if context:
            print(f"[send_message_to_qachat] session 정보를 DB에서 불러옵니다")
            print(f"context: {context}")
            context = cast(SummaryType, json.loads(context))
            summary = context["summary"]
            messages = messages_from_dict(context["messages"])
            qachat.load_memory(session_id, summary, messages)
        else:
            print("session 정보가 없습니다. 새로운 context를 생성합니다.")

    bookmarks = db_get_bookmarked_movies(db, user_id)
    archives = db_get_archived_movies(db, user_id)
    
    async def generator():
        response = ""
        async for chunk in qachat.get_streamed_messages(session_id, titles, message, bookmarks, archives):
            response += chunk
            yield { "type": "message", "content": chunk }
        yield { "type": "signal", "content": "chat done" }
        
        ids: list[int]= []
        hints = qachat.extract_suggested_titles_and_metadata_with_llm(response)
        for hint in hints:
            title = hint.get("title")
            keyword = hint.get("keyword")
            assert(title)
            
            movie = fuzzy_search(db, title, keyword)
            if movie is not None:
                ids.append(movie.id)

        yield { "type": "recommendation", "content": ids }
    
    return generator()

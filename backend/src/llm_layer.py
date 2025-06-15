import llm.qachat as qachat
import llm.crawler as crawler
from database.utils import *
import json
from langchain.schema import messages_to_dict, messages_from_dict
from typing import AsyncGenerator, TypedDict

from database.chroma import *
from datetime import datetime, timezone
from sse import *

class SummaryType(TypedDict):
    """
    대화방의 대화 내역의 필요한 정보를 담고 있는 opaque type
    """
    summary: str
    messages: list[dict]

def is_room_immersive(room: ChatRoomInfoInternal) -> bool:
  return bool(room.character_id)


def get_current_summary(room: ChatRoomInfoInternal) -> SummaryType:
    import llm.characterchat as cc
    
    session_id = str(room.id)
    
    # characterchat.py의 session 메모리 공간과
    # qachat.py의 session 메모리 공간이 분리되어 있어,
    # 다음과 같이 처리해줘야 합니다. 아마 통합해도 될 것 같긴 한데,
    # 다른 side-effect가 발생할 수도 있어 일단은 이렇게 처리.
    if is_room_immersive(room):
        memory = cc.get_memory(session_id)
    else:
        memory = qachat.get_memory(session_id)

    summary = memory.moving_summary_buffer
    messages = memory.chat_memory.messages
    messages_dict = messages_to_dict(messages)
    return { "summary": summary, "messages": messages_dict }

# 유저 입력을 전처리하는 함수
# ..로 의도되었으나, 현재는 아무것도 안 하는 함수.
# 일단은 혹시 몰라 남겨둠.
def _preprocess_user_input(user_input: str) -> str:
    return user_input

async def send_message_to_ai(db: Session, user_id: int, room_id: int, message: str):
    """
    message를 AI agent에게 전송하고, 그 응답을 하나의 string으로 반환합니다.  
    비동기 함수이기 때문에 응답을 받을 때는 `await`를 사용해주세요.
    """
    full_answer = ""
    movie_ids = []
    
    async for chunk in stream_send_message_to_ai(db, user_id, room_id, message):
        t = sse_type(chunk)
        v = sse_content(chunk)
        if t == SSE_MESSAGE:
            full_answer += v if v else ""
        elif t == SSE_RECOMMEND:
            movie_ids = v

    return { "message": full_answer, "recommendation": movie_ids }

# fast-path
def fuzzy_fast(db: Session, title: str, keyword: str|None):
    meta = chroma_fuzzy_search(title, [keyword] if keyword else None)
    if meta:
        movie = db_find_movie_by_id(db, meta.sqlite_id, True)
        return movie, meta
    return None, None

# slow-path
def fuzzy_slow(db: Session, title: str, keyword: str|None, meta: MovieMeta|None):
    movie = None
    if meta:
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

    return movie

async def stream_create_character(db: Session, room_id: int, character_id: int):
    """
    character_id, room_id가 반드시 존재해야 합니다.
    """
    import llm.characterchat as cc

    session_id = str(room_id)

    profile = cast(
        CharacterInfoInternal,
        db_get_character_profile_by_id(db, character_id)
    )
    
    if profile.description:
        yield make_sse(SSE_SIGNAL, SSE_CC_DONE)
        return
    
    movie = db_find_movie_by_id(db, profile.movie_id, False)
    if movie is None:
        yield make_sse(SSE_SIGNAL, SSE_CC_FAIL)
        return

    title = movie.title
    character = profile.name

    if not cc.is_cached_on_chroma(title, session_id):
        if not movie.wiki_document:
            yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
            movie.wiki_document = crawler.get_wikipedia_content(title) or crawler.get_wikipedia_content(title + " (영화)")
            if movie.wiki_document:
                db_update_wikipedia_data(db, movie.id, movie.wiki_document)
            yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

        cc.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, session_id)
    
    yield make_sse(SSE_SIGNAL, SSE_CC_START)
    personality = cc.create_personality(title, character, session_id)
    cc.set_character_prompts(session_id, personality)
    if not db_update_character_description(db, character_id, personality):
        yield make_sse(SSE_SIGNAL, SSE_CC_FAIL)
    else:
        yield make_sse(SSE_SIGNAL, SSE_CC_DONE)


async def stream_character_chat(db: Session, room_id: int, message: str, character_id: int) -> AsyncGenerator[dict[str, Any], Any]:
    import llm.characterchat as cc
    """
    캐릭터 채팅 모드 스트리밍
    """
    session_id = str(room_id)
    
    # 캐릭터 프로필 로드
    character_profile = db_get_character_profile_by_id(db, character_id)  # 이 함수가 DB utils에 있다고 가정
    if not character_profile or not character_profile.description:
        yield make_sse(SSE_MESSAGE, "캐릭터 정보를 찾을 수 없습니다.")
        return
    
    # 세션에 캐릭터 프롬프트 설정
    cc.set_character_prompts(session_id, character_profile.description)
    
    # 메모리 로드 (기존 대화 기록)
    if not cc.is_memory_on_cache(session_id):
        print(f"[cc] session cache가 비어있습니다")
        context = db_get_chatroom_context(db, room_id).summary
        if context:
            print(f"[cc] session 정보를 DB에서 불러옵니다")
            print(f"context: {context}")
            context = cast(SummaryType, json.loads(context))
            summary = context["summary"]
            messages = messages_from_dict(context["messages"])
            cc.load_memory(session_id, summary, messages)
        else:
            print("session 정보가 없습니다. 새로운 context를 생성합니다.")
    
    # 응답 생성
    yield make_sse(SSE_SIGNAL, SSE_MESSAGE_START)
    response = ""
    async for chunk in cc.get_cc_response(session_id, message):
        response += chunk
        yield make_sse(SSE_MESSAGE, chunk)
    yield make_sse(SSE_SIGNAL, SSE_MESSAGE_END)


async def stream_send_message_to_ai(db: Session, user_id: int, room_id: int, message: str) -> AsyncGenerator[dict[str, Any], Any]:
    """
    message를 AI agent에게 전송하고, 그 응답을 stream 모드로 반환하는 AsyncGenerator를 반환합니다  
    room_id의 ChatRoom이 immersive인지 아닌지는 함수 내부에서 자동으로 처리되기 때문에, 일관적으로 호출하시면 됩니다.
    """
    # 채팅방이 몰입형인지 확인
    room = db_get_chatroom(db, room_id)
    if room.character_id:
        async for chunk in stream_character_chat(db, room_id, message, room.character_id):
            yield chunk
        return

    # 채팅방 ID를 session ID로 사용합니다.
    session_id = str(room_id)
    
    message = _preprocess_user_input(message)
    titles: list[str] = []
    hints = qachat.extract_titles_and_metadata_with_llm(message)
    if hints and hints[0] == '제목이 명확하지 않음 사용자에게 재입력 요청':
        titles = cast(list[str], hints)
    else:
        for hint in hints:
            title = hint.get("title")
            keyword = hint.get("keyword")
            assert(title)

            if qachat.is_cached_on_chroma(title, session_id):
                continue

            movie, meta = fuzzy_fast(db, title, keyword)
            if not movie:
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                movie = fuzzy_slow(db, title, keyword, meta)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

            if movie is None:
                continue
            
            print(f"[send_message_to_qachat] db_data:\n{movie}\n\n")
            
            # 4. See if we have any outdated, or missing data in our DB
            if not movie.wiki_document:
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                movie.wiki_document = crawler.get_wikipedia_content(title)
                if movie.wiki_document:
                    db_update_wikipedia_data(db, movie.id, movie.wiki_document)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

            # 5. 영화 리뷰를 불러옵니다. 3번째 인자를 None이 아닌 것으로 설정하면 그 수만큼만 리뷰를 불러옵니다
            reviews = None # 영화가 여러 개 일 때 첫번째 영화의 리뷰만 불러오는 오류 해결
            reviews = db_get_movie_reviews(db, movie.id, None)
            if reviews != None:
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                print(f"{title}에 대한 리뷰가 DB에 없습니다. 리뷰를 크롤링 합니다...")
                reviews = cast(list[str], crawler.get_watcha_reviews(title))
                db_add_movie_reviews(db, movie.id, reviews)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

            # 6. Let's cache it
            qachat.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, reviews, session_id)
            print(f"[send_message_to_qachat] chroma에 {title}(이)가 캐시되었습니다")

        if not hints:
            print(f"[send_message_to_qachat] 감지된 영화 없음")

    
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
    
    # AI 응답 생성
    yield make_sse(SSE_SIGNAL, SSE_MESSAGE_START)
    response = ""
    async for chunk in qachat.get_streamed_messages(session_id, titles, message, bookmarks, archives):
        response += chunk
        yield make_sse(SSE_MESSAGE, chunk)
    yield make_sse(SSE_SIGNAL, SSE_MESSAGE_END)
    
    # 추천 영화 추출
    hints = qachat.extract_suggested_titles_and_metadata_with_llm(response)
    if hints and hints[0] == '제목이 명확하지 않음 사용자에게 재입력 요청':
        pass
    elif hints:
        ids: list[int]= []
        for hint in hints:
            title = hint.get("title")
            keyword = hint.get("keyword")
            assert(title)
            
            yield make_sse(SSE_SIGNAL, SSE_DB_START)
            movie, meta = fuzzy_fast(db, title, keyword)
            yield make_sse(SSE_SIGNAL, SSE_DB_END)
            if not movie:
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                movie = fuzzy_slow(db, title, keyword, meta)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

            if movie is not None:
                ids.append(movie.id)

        yield make_sse(SSE_RECOMMEND, ids)

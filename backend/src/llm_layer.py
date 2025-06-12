from llm.tools import get_current_subject, get_recommendations
import llm.qachat as qachat
import llm.crawler as crawler
from database.utils import *
import json
from langchain.schema import messages_to_dict, messages_from_dict
from typing import AsyncGenerator, TypedDict

from database.chroma import *
from datetime import datetime, timezone
from sse import *
from common.logging_config import logger

class SummaryType(TypedDict):
    """
    대화방의 대화 내역의 필요한 정보를 담고 있는 opaque type
    """
    summary: str
    messages: list[dict]

def is_room_immersive(room: ChatRoomInfoInternal) -> bool:
  return bool(room.character_id)


def get_summary_from_qachat(room: ChatRoomInfoInternal) -> SummaryType:
    import llm.characterchat as cc
    
    session_id = str(room.id)
    
    if is_room_immersive(room):
        memory = cc.get_memory(session_id)
    else:
        memory = qachat.get_memory(session_id)

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
    
    async for chunk in stream_send_message_to_qachat(db, user_id, room_id, message):
        t = sse_type(chunk)
        v = sse_content(chunk)
        if t == SSE_MESSAGE:
            full_answer += v if v else ""
        elif t == SSE_RECOMMEND:
            movie_ids = v

    return { "message": full_answer, "recommendation": movie_ids }

def fuzzy_fast(db: Session, title: str, keyword: dict|None):
    meta = chroma_fuzzy_search(title, keyword)
    logger.info(meta)
    if meta:
        movie = db_find_movie_by_id(db, meta.sqlite_id, True)
        return movie, meta
    return None, None

def fuzzy_slow(db: Session, title: str, keyword: dict|None, meta: MovieMeta|None):
    movie = None
    logger.info("slow path")
    if meta:
        if meta.tmdb_id is not None:
            movie = update_movie_by_tmdb_id(db, meta.tmdb_id)
        else:
            movies = update_movie_by_tmdb_search(db, search={
                "query": meta.title,
                "primary_release_year": str(meta.year) if meta.year else "",
            })
            if len(movies) > 0:
                movie = movies[0]

        if movie:
            chroma_delete(meta)
            meta.sqlite_id = movie.id
            meta.tmdb_id = movie.tmdb_id
            meta.created_at = datetime.now(timezone.utc).isoformat()
            meta.title = movie.title
            if movie.release_date:
                meta.year = movie.release_date.year
            chroma_insert(meta)
        else:
            chroma_delete(meta)
            return
        
    else:
        logger.info("????")
        movies = update_movie_by_tmdb_search(db, search={
            "query": title,
            "primary_release_year": keyword["year"] if keyword and keyword.get("year") else ""
        })
        if len(movies) == 0:
            return

        movie = movies[0]
        chroma_insert(MovieMeta(
            sqlite_id=movie.id,
            tmdb_id=movie.tmdb_id,
            series=keyword["series"] if keyword and keyword.get("series") else 1,
            title=movie.title,
            year=movie.release_date.year if movie.release_date else None,
            created_at=movie.last_update.isoformat()
        ))

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


async def stream_send_message_to_qachat(db: Session, user_id: int, room_id: int, message: str) -> AsyncGenerator[dict[str, Any], Any]:
    """
    message를 AI agent에게 전송하고, 그 응답을 stream 모드로 반환하는 AsyncGenerator를 반환합니다
    """
    # 채팅방이 몰입형인지 확인
    room = db_get_chatroom(db, room_id)
    if room.character_id:
        async for chunk in stream_character_chat(db, room_id, message, room.character_id):
            yield chunk
        return

    # 채팅방 ID를 session ID로 사용합니다.
    session_id = str(room_id)
    logger.info(f"*********************************************************")
    
    logger.info(f"user message: {message}")
    message = _preprocess_user_input(message)
    titles: list[str] = []
    context = db_get_chatroom_context(db, room_id).summary
    if context:
        context = cast(SummaryType, json.loads(context))
        history = messages_from_dict(context["messages"])
    else:
        history = []

    subjects = get_current_subject(history, message)
    if subjects and subjects[0].confidence < 0.3:
        logger.info(f"title이 명확하지 않음: \n{subjects}")
        titles = ['제목이 명확하지 않음 사용자에게 재입력 요청']
    else:
        logger.info(f'인식된 title({len(subjects)}): {subjects}')

        # we take a heuristic approach; if we think we did it enough, stop over-researching
        primary_threshold = 0.85
        secondary_threshold = 0.65
        for subject in subjects:
            if not subject.title:
                continue
            
            title = subject.title
            year = subject.year
            series = subject.series

            if subject.confidence < secondary_threshold:
                break # stop. just stop...
            
            movie, meta = fuzzy_fast(db, title, keyword={ "year": year, "series": series })
            if movie:
                logger.info(f"{title}={movie.title} FUZZY MATCHED!!")
            else:
                logger.info(f"{title} FUZZY MATCH FAILED")
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                movie = fuzzy_slow(db, title, { "year": year, "series": series }, meta)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)
                if movie:
                    logger.info(f"{title}에 대한 WEB 검색 성공 {movie.title}")
                else:
                    logger.info(f"{title}에 대한 WEB 검색 실패")
                    continue
            
            title = movie.title # we will use more 'accurate' title from now on

            if subject.confidence >= primary_threshold:
                # 4. See if we have any outdated, or missing data in our DB
                if not movie.wiki_document:
                    logger.info(f"{title}에 대한 Wikipedia 크롤링 실시")
                    yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                    movie.wiki_document = crawler.get_wikipedia_content(title)
                    if movie.wiki_document:
                        db_update_wikipedia_data(db, movie.id, movie.wiki_document)
                        logger.info(f"{title}에 대한 Wikipedia 크롤링 성공")
                    else:
                        logger.info(f"{title}에 대한 Wikipedia 크롤링 실패")

                    yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

                # 5. 영화 리뷰를 불러옵니다. 3번째 인자를 None이 아닌 것으로 설정하면 그 수만큼만 리뷰를 불러옵니다
                reviews = None # 영화가 여러 개 일 때 첫번째 영화의 리뷰만 불러오는 오류 해결
                reviews = db_get_movie_reviews(db, movie.id, None)
                if not reviews:
                    logger.info(f"{title}에 대한 Watcha 크롤링 실시")
                    yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                    reviews = cast(list[str], crawler.get_watcha_reviews(title))
                    if reviews:
                        logger.info(f"{title}에 대한 Watcha 크롤링 성공")
                    else:
                        logger.info(f"{title}에 대한 Watcha 크롤링 실패")

                    db_add_movie_reviews(db, movie.id, reviews)
                    yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)
            
                logger.info(f"{title}에 대한 모든 정보 획득")

                # 6. Let's cache it
                if not qachat.exist_in_chroma(title, session_id):
                    qachat.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, reviews, session_id)
                    logger.info(f"{title}이 chromaDB에 캐시되었음")
            else:
                logger.info(f"{title} 크롤링이 deferred 되었음")

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
    
    logger.info("=======================추천 기능 시작=================")
    
    # 추천 영화 추출
    recommended = get_recommendations(response)
    if recommended:
        ids: list[int]= []
        for movie in recommended:
            title = movie.title
            year = movie.year
            series = movie.series
            assert(title)
            
            keywords = {}
            if year:
                keywords["year"] = year
            elif series:
                keywords["series"] = series
            
            logger.info(f"추천된 영화: {title}")
            
            yield make_sse(SSE_SIGNAL, SSE_DB_START)
            movie, meta = fuzzy_fast(db, title, keywords)
            yield make_sse(SSE_SIGNAL, SSE_DB_END)
            if not movie:
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_START)
                movie = fuzzy_slow(db, title, keywords, meta)
                yield make_sse(SSE_SIGNAL, SSE_CRAWL_END)

            if movie is not None:
                ids.append(movie.id)

        yield make_sse(SSE_RECOMMEND, ids)

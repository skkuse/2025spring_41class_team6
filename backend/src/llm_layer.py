import llm.qachat as qachat
import llm.crawler as crawler
from database.utils import *
import json
from langchain.schema import messages_to_dict, messages_from_dict
from typing import TypedDict

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

def stream_send_message_to_qachat(db: Session, user_id: int, room_id: int, message: str):
    """
    message를 AI agent에게 전송하고, 그 응답을 stream 모드로 반환하는 AsyncGenerator를 반환합니다
    """
    # 채팅방 ID를 session ID로 사용합니다.
    session_id = str(room_id)
    
    message = _preprocess_user_input(message)
    titles: list[str] = []
    ids: list[int] = []
    hints = qachat.extract_titles_and_metadata_with_llm(message)
    
    # 제목이 명확할 경우에만 데이터를 가져옵니다.
    if hints[0] == '제목이 명확하지 않음 사용자에게 재입력 요청':
        titles = hints
        
    elif hints:
        print(f"[send_message_to_qachat] 감지된 영화 제목: {hints}")
        
        # llm.qachat.load_data 로직 + Moviechat DB 저장
        for hint in hints:
            title = hint.get("title")
            keyword = hint.get("keyword")
            assert(title)
            if keyword is None:
                keyword = ""
            
            titles.append(title)
            
            # 1. Let's see if it is cached on chroma
            if qachat.is_cached_on_chroma(title, session_id):
                continue
            
            # 2. Too bad it wasn't cached. It's time to look inside our DB...
            movies_in_db = db_find_movies_by_alias(db, title)
            
            # 3. Seems like we didn't have any. We need to find it on the web
            if len(movies_in_db) == 0:
                movies_in_db = update_movie_by_tmdb_search(db, search={ "query": title, "primary_release_year": keyword })
                if len(movies_in_db) == 0:
                    continue
            
            # 여러 movie들이 TMDB에서 나올 수 있음
            # TODO: 연도별 기반 매칭, IMDB 이용
            movie = movies_in_db[0]

            print(f"[send_message_to_qachat] db_data:\n{movie}\n\n")
            
            # 4. See if we have any outdated, or missing data in our DB
            if not movie.wiki_document:
                movie.wiki_document = crawler.get_wikipedia_content(title)
                if movie.wiki_document:
                    db_update_wikipedia_data(db, movie.id, movie.wiki_document)

            # 5. 영화 리뷰를 불러옵니다. 3번째 인자를 None이 아닌 것으로 설정하면 그 수만큼만 리뷰를 불러옵니다
            reviews = None # 영화가 여러 개 일 때 첫번째 영화의 리뷰만 불러오는 오류 해결
            reviews = db_get_movie_reviews(db, movie.id, None)
            if reviews != None:
                print(f"{title}에 대한 리뷰가 DB에 없습니다. 리뷰를 크롤링 합니다...")
                reviews = cast(list[str], crawler.get_watcha_reviews(title))
                db_add_movie_reviews(db, movie.id, reviews)

            # 6. Let's cache it
            qachat.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, reviews, session_id)
            print(f"[send_message_to_qachat] chroma에 {title}(이)가 캐시되었습니다")

    else:
        print(f"[send_message_to_qachat] 감지된 영화 제목이 없습니다.")
    
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
            if keyword is None:
                keyword = ""
            
            movies_in_db = db_find_movies_by_alias(db, title)
            
            # 3. Seems like we didn't have any. We need to find it on the web
            if len(movies_in_db) == 0:
                movies_in_db = update_movie_by_tmdb_search(db, search={ "query": title, "primary_release_year": keyword })
                if len(movies_in_db) == 0:
                    continue
            
            # 여러 movie들이 TMDB에서 나올 수 있음
            movie = movies_in_db[0]
            ids.append(movie.id)

        yield { "type": "recommendation", "content": ids }
    
    return generator()

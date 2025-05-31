import llm.qachat as qachat
import llm.crawler as crawler
from database.utils import *
import json
from langchain.schema import messages_to_dict, messages_from_dict

def _preprocess_user_input(user_input: str) -> str:
    return user_input

def get_summary_from_qachat(room_id: int) -> dict:
    memory = qachat.get_memory(str(room_id))
    summary = memory.moving_summary_buffer
    messages = memory.chat_memory.messages
    messages_dict = messages_to_dict(messages)
    return { "summary": summary, "messages": messages_dict }

def send_message_to_qachat(db: Session, user_id: int, room_id: int, message: str) -> str:
    """
    
    """
    message = _preprocess_user_input(message)
    titles = qachat.extract_titles_with_llm(message)
    if titles:
        print(f"[send_message_to_qachat] 감지된 영화 제목: {titles}")
        
        # llm.qachat.load_data 로직 + Moviechat DB 저장
        for title in titles:
            
            # 1. Let's see if it is cached on chroma
            if qachat.is_cached_on_chroma(title):
                continue
            
            # 2. Too bad it wasn't cached. It's time to look inside our DB...
            movies_in_db = db_find_movies_by_alias(db, title)
            
            # 3. Seems like we didn't have any. We need to find it on the web
            if len(movies_in_db) == 0:
                movies_in_db = update_movie_by_tmdb_search(db, search={ "query": title })
                if len(movies_in_db) == 0:
                    continue
            
            # 여러 movie들이 TMDB에서 나올 수 있음
            # TODO: 연도별 기반 매칭, IMDB 이용
            movie = movies_in_db[0]

            db_data_modified = False
            print(f"[send_message_to_qachat] db_data:\n{movie}\n\n")
            
            # 4. See if we have any outdated, or missing data in our DB
            if not movie.wiki_document:
                movie.wiki_document = crawler.get_wikipedia_content(title)
                db_data_modified = True
            
            # 5. we just crawl watcha reviews unconditionally for now...
            reviews = crawler.get_watcha_reviews(title)
            
            # 6. we should update our DB if it was modified(not yet implemented)
            if db_data_modified:
                pass

            # 7. Let's cache it
            qachat.add_to_chroma(title, movie.tmdb_overview, movie.wiki_document, reviews)
            print(f"[send_message_to_qachat] chroma에 {title}(이)가 캐시되었습니다")

    else:
        print(f"[send_message_to_qachat] 감지된 영화 제목이 없습니다.")
    
    # 채팅방 ID를 session ID로 사용합니다.
    session_id = str(room_id)

    if not qachat.is_memory_on_cache(session_id):
        print(f"[send_message_to_qachat] session을 LOAD합니다")
        context = db_get_chatroom_context(db, room_id).summary
        if context:
            print(f"context: {context}")
            context = json.loads(context)
            summary = context["summary"]
            messages = messages_from_dict(context["messages"])
            qachat.load_memory(session_id, summary, messages)

    qa_chain = qachat.get_qa_chain(session_id, target_titles=titles)
    result = qa_chain.invoke({ "query": message })
    return result["result"]


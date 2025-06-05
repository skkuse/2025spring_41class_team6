import os
from dotenv import load_dotenv

import tmdbsimple as tmdb
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationSummaryBufferMemory


from llm.crawler import get_tmdb_overview, get_wikipedia_content, get_watcha_reviews

# --------------------- [1] 초기 설정 ---------------------
load_dotenv()
tmdb.API_KEY = os.environ.get("TMDB_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
if not tmdb.API_KEY or not openai_key:
    raise ValueError("API 키가 없습니다.")

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
embedding = OpenAIEmbeddings()

# --------------------- [2] 프롬프트 ---------------------

title_extract_prompt = PromptTemplate.from_template("""
다음 문장에서 언급된 영화 제목을 출력하세요. 
특히 시리즈물이라면 몇 번 시리즈인지 숫자를 기반으로 명확히 구분해주세요.
만일 영화 관련 내용이 아니라면 '없음'이라고 답변하세요.
각 영화 제목은 , 로 구분하세요.
각 영화에 대해 다음 정보를 포함하세요:

- 영화 제목
- 구분 가능한 키워드 또는 정보 (출시년도, 시리즈 번호, 넷플릭스/디즈니 등 플랫폼)

출력 형식: 영화제목1 (키워드1), 영화제목2 (키워드2) ...

예시:
듄 (2021), 듄 2 (2024), 바비 (마고 로비 주연)

문장: {user_input}
영화 목록:
""")

title_chain = title_extract_prompt | llm

response_prompt = PromptTemplate.from_template("""
이전 대화 요약:
{history}
아래의 영화 정보와 리뷰들을 참고해 사용자 질문에 답하세요.
리뷰에 포함된 다양한 관점을 반영해 **토론하듯 풍부하게 설명**하세요.
리뷰의 내용을 가져올 때는 왓챠피디아에서 가져온 내용이라는 것을 명시해주세요.
질문이 아니면 자연스럽게 대화를 이어가세요.
사용자가 영화를 추천해달라고 요청하면 이전 대화기록과 리뷰를 바탕으로 사용자가 본 적이 없는 비슷한 영화들을 추천해주세요.
추천할 영화 리스트는 "[영화 추천 리스트] 영화제목1, 영화제목2, 영화제목3 ..."의 형식으로 대화의 맨 앞에 표시한 후 대화를 이어가 주세요. 

당신은 영화 전문가 AI입니다. 사용자의 모든 질문에 마크다운 형식으로 답변해주세요.
**답변 구조:**
- 제목으로 섹션 구분
- 제목은 마크다운 제목 형식으로 작성
- 2-3문장마다 줄바꿈
- 관련 정보 그룹핑
- 핵심 정보 우선 배치

사용자가 이해하기 쉽고 시각적으로 깔끔한 답변을 제공해주세요.
친구와 얘기하듯이 친절하고 친밀하게 답변해주세요.
{context}

질문: {question}
답변:
""")

# --------------------- [3] LLM 기반 영화 제목 추출 함수 ---------------------
def extract_titles_and_metadata_with_llm(user_input: str) -> list[dict]:
    response = title_chain.invoke({"user_input": user_input})
    raw_result = response.content.strip().replace("\n", "")
    print("[extract_titles...] " + user_input)
    print("[extract_titles...] " + response.content.strip())
    print("[extract_titles...] " + raw_result)

    if not raw_result or raw_result.lower() in {"없음", "해당 없음", "모름", "영화 아님"}:
        return []

    # 결과 파싱: "듄 (2021), 바비 (마고 로비 주연)" 등에서 → [{title: "듄", keyword: "2021"}, ...]
    entries = [e.strip() for e in raw_result.split(",") if e.strip()]
    parsed = []
    for entry in entries:
        if "(" in entry and ")" in entry:
            title, keyword = entry.split("(", 1)
            parsed.append({"title": title.strip(), "keyword": keyword.strip(" )")})
        else:
            parsed.append({"title": entry.strip(), "keyword": ""})
    return parsed

def search_tmdb_movie(title: str, keyword: str = "") -> dict:
    search = tmdb.Search()
    response = search.movie(query=title)
    results = response.get('results', [])

    if not results:
        return {}

    # 키워드 필터링 우선 적용 (연도/키워드가 결과에 있는지)
    if keyword:
        for movie in results:
            if keyword in (movie.get("release_date", "") or "") or keyword.lower() in movie.get("overview", "").lower():
                return {
                    "tmdb_id": movie["id"],
                    "title": movie["title"],
                    "release_date": movie.get("release_date", ""),
                }
                
    movie = results[0]
    return {
        "tmdb_id": movie["id"],
        "title": movie["title"],
        "release_date": movie.get("release_date", ""),
    }

def get_validated_movies(user_input: str) -> list[dict]:
    movie_infos = extract_titles_and_metadata_with_llm(user_input)
    validated = []
    for m in movie_infos:
        movie = search_tmdb_movie(m["title"], m["keyword"])
        if movie:
            validated.append(movie)
    return validated

# --------------------- [4] Chroma 데이터 로딩 ---------------------
def _is_cached_on_chroma(title: str, db):
    try:
        existing_titles = {doc.metadata['title'] for doc in db.similarity_search("영화", k=50)}
    except:
        existing_titles = set()
    return title in existing_titles

def is_cached_on_chroma(title: str):
    return _is_cached_on_chroma(title, get_chroma_shared())

def _add_to_chroma(movie_name: str, overview: str, wiki: str, reviews: list[str], db):
    joined_reviews = "\n\n".join(f"- {r}" for r in reviews)

    combined = f"[영화 제목] {movie_name}\n\n[TMDB 줄거리]\n{overview}\n\n[Wikipedia 문서]\n{wiki}\n\n[왓챠 리뷰]\n{joined_reviews}"
    doc = Document(page_content=combined, metadata={"title": movie_name})

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents([doc])
    db.add_documents(split_docs)

def add_to_chroma(title: str, tmdb_overview: str|None, wikipedia_content: str|None, watcha_reviews: list[str]):
    if not tmdb_overview:
        tmdb_overview = ""
    if not wikipedia_content:
        wikipedia_content = ""
    _add_to_chroma(title, tmdb_overview, wikipedia_content, watcha_reviews, get_chroma_shared())
     
def load_data(titles, db):
    for movie_name in titles:
        if _is_cached_on_chroma(movie_name, db):
            print(f"[스킵됨] '{movie_name}'은 이미 Chroma에 저장되어 있습니다.")
            return

        print(f"[저장됨] '{movie_name}'에 대해 새로 검색합니다.")
        
        overview = get_tmdb_overview(movie_name)
        wiki = get_wikipedia_content(movie_name) or get_wikipedia_content(movie_name + " (영화)")
        reviews = get_watcha_reviews(movie_name, max_comments=20)
        _add_to_chroma(movie_name, overview, wiki, reviews, db)

# --------------------- [5] Chroma & Memory 설정 ---------------------
_cached_chroma = None
session_memories = {}

def get_chroma_shared():
    global _cached_chroma
    if _cached_chroma is None:
        os.makedirs("./chroma_data/movie", exist_ok=True)
        _cached_chroma = Chroma(
            persist_directory="./chroma_data/movie",
            embedding_function=embedding
        )
    return _cached_chroma

def is_memory_on_cache(session_id):
    return session_id in session_memories

def load_memory(session_id: str, summary: str, messages: list):
    memory = ConversationSummaryBufferMemory(
        llm=ChatOpenAI(temperature=0),
        return_messages=True,
        max_token_limit=1000
    )
    memory.moving_summary_buffer= summary
    memory.chat_memory.messages = messages
    session_memories[session_id] = memory

def get_memory(session_id):
    if session_id not in session_memories:
        session_memories[session_id] = ConversationSummaryBufferMemory(
            llm=ChatOpenAI(temperature=0),
            return_messages=True,
            max_token_limit=1000
        )
    return session_memories[session_id]

# --------------------- [6] 스트리밍 응답 처리 함수 ---------------------
# 기존 RetrievalQA 체인을 사용하지 않고, context를 직접 구성한 뒤 ChatOpenAI(stream=True)로 토큰 단위 출력
from typing import Iterator

def stream_chat_response(prompt_text: str) -> Iterator[str]:
    streaming_llm = ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True)
    for chunk in streaming_llm.stream(prompt_text):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content

# --------------------- [7] 메인 루프 ---------------------
def run_qa_mode():
    session_id = "session456"
    while True:
        user_input = input("\n질문을 입력하세요 (종료하려면 'exit'): ")
        if user_input.lower() == "exit":
            break

        validated_movies = get_validated_movies(user_input)
        movie_titles = [m["title"] for m in validated_movies]

        for m in validated_movies:
            print(f"✔ {m['title']} ({m['release_date']}) → TMDB ID: {m['tmdb_id']}")

        if movie_titles:
            chroma = get_chroma_shared()
            load_data(movie_titles, chroma)
        else:
            print("[안내] 영화 data loading 생략.")

        # 충돌 해결: 스트리밍 구조 기준으로 db/memory 가져오고 retriever 구성
        db = get_chroma_shared()
        memory = get_memory(session_id)

        search_kwargs = {"k": 10}
        if movie_titles:
            search_kwargs["filter"] = {"title": {"$in": movie_titles}}
        retriever = db.as_retriever(search_kwargs=search_kwargs)

        docs = retriever.get_relevant_documents(user_input)
        context = "\n\n".join([doc.page_content for doc in docs])

        summary = memory.buffer or "(요약 없음)"
        full_prompt = response_prompt.format(history=summary, context=context, question=user_input)
        
        print("\n[답변] ", end="", flush=True)
        full_answer = ""
        for token in stream_chat_response(full_prompt):
            print(token, end="", flush=True)
            full_answer += token
        print()

        # 요약 memory 업데이트
        memory.save_context({"input": user_input}, {"output": full_answer})
        summary = memory.buffer
        #if summary:
        #    print("\n[요약] 지금까지의 대화 요약:\n", summary)

# llm_layer에서 사용하는 함수입니다.
# run_qa_mode의 로직을 일부 사용하며, 비동기적으로 user에게 message를 전달하는 역할을 합니다.
# run_qa_mode와 사실 상 동일한 중복 코드이나, 혼란을 방지하기 위해 run_qa_mode는 남겨놓았습니다.
# 만약 변경 사항이 있다면, run_qa_mode말고 여기를 고쳐 주세요
# 그리고 웬만하면 입력 parameter랑 return 형식을 바꾸지 말아주세요
# llm_layer에서 의존하고 있는 함수 목록:
#   * get_memory()
#   * extract_titles_and_metadata_with_llm()
#   * is_cached_on_chroma()
#   * add_to_chroma()
#   * is_memory_on_cache()
#   * load_memory()
# 위 함수들은 동작 변경을 가급적 하지 않아주셨으면 합니다.
# 궁금하신 점 있으면 말씀해주세요!
from typing import List
from database.utils import MovieInfoInternal
def get_streamed_messages(
        session_id: str,
        movie_titles: list[str],
        user_input: str,
        bookmark: List[MovieInfoInternal],
        archive: List[MovieInfoInternal]):
    
    #
    # session_id Summary를 사용하는데 쓰일 session_id 입니다.
    # movie_titles은 extract_with_llm... 함수로 추출해서 나온 title들의 배열입니다.
    # user_input는 그냥 사용자 입력입니다. 채팅창에 사용자가 입력한 그 문자열 그대롭니다.
    #
    # 북마크 정보와 아키이브된 영화 정보는 bookmark, archive를 통해 전달됩니다.
    # bookmark, archive는 영화 정보의 list로, bookmark[0], bookmark[1] 이런 식으로 참조할 수 있습니다.
    # 각 element는 pydantic으로 typing이 들어가 있기 때문에, Ctrl(CMD)+Click으로 안에 어떤 필드가 있는지
    # 확인해보실 수 있습니다. 따라서 title이 필요하다면 bookmark[0].title 이렇게 바로 쓸 수 있습니다.
    #
    # 만약에 일반 dict 형식으로 바꾸고 싶으시다면:
    # res = bookmark[0].model_dump()
    # 이렇게 하시면 res가 dict로 변환된 형식이 됩니다.
    #
    # 참고: 아직 archive 기능이 미완이라 일단 빈 배열만 보내고 있을 거라서 참고바랍니다.
    #
    # 이 함수 및 _stream_response_generator를 수정해서 bookmark 반영이 되게 해주시면 될 것 같습니다.
    # _stream_response_generator의 입력 parameter는 바뀌어도 괜찮지만,
    # get_stream_messages의 입력 parameter, return 타입,
    # _stream_response_generator의 return 타입이 변경되면 안 됩니다.
    #

    db = get_chroma_shared()
    memory = get_memory(session_id)

    search_kwargs = {"k": 10}
    if movie_titles:
        search_kwargs["filter"] = {"title": {"$in": movie_titles}}
    retriever = db.as_retriever(search_kwargs=search_kwargs)

    docs = retriever.get_relevant_documents(user_input)
    context = "\n\n".join([doc.page_content for doc in docs]) or "관련된 문서를 찾을 수 없습니다."

    summary = memory.buffer or "(요약 없음)"
    full_prompt = response_prompt.format(history=summary, context=context, question=user_input)
    
    return _stream_response_generator(user_input, full_prompt, memory)

import json

async def _stream_response_generator(user_input: str, prompt: str, memory):
    full_answer = ""
    streaming_llm = ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True)
    for chunk in streaming_llm.stream(prompt):
        if hasattr(chunk, "content") and chunk.content:
            content = (
                chunk.content if isinstance(chunk.content, str)
                else json.dumps(chunk.content, ensure_ascii=False)
            )
            full_answer += content
            yield content # content를 받는 대로 client에게 보냅니다

    # content를 전부 받고 나면, save_context가 호출됩니다
    memory.save_context({"input": user_input}, {"output": full_answer})

suggest_extract_prompt = PromptTemplate.from_template("""
당신은 영화 전문가 AI 입니다.
다음 문장에서 AI가 인간에게 추천 해준 영화 제목들을 출력하세요.
특히 시리즈물이라면 몇 번 시리즈인지 숫자를 기반으로 명확히 구분해주세요.
만일 문장 안에서 AI가 추천한 영화가 없다면, '없음'이라고 답변하세요.
각 영화 제목은 , 로 구분하세요.
각 영화에 대해 다음 정보를 포함하세요:

- 영화 제목
- 구분 가능한 키워드 또는 정보 (출시년도, 시리즈 번호, 넷플릭스/디즈니 등 플랫폼)

출력 형식: 영화제목1 (키워드1), 영화제목2 (키워드2) ...

예시:
듄 (2021), 듄 2 (2024), 바비 (마고 로비 주연)

문장: {user_input}
영화 목록:
""")

suggest_chain = suggest_extract_prompt | llm

def extract_suggested_titles_and_metadata_with_llm(user_input: str) -> list[dict]:
    response = suggest_chain.invoke({"user_input": user_input})
    raw_result = response.content.strip().replace("\n", "")
    print("[추천된 영화]" + response.content.strip())

    if not raw_result or raw_result.lower() in {"없음", "해당 없음", "모름", "영화 아님"}:
        return []

    # 결과 파싱: "듄 (2021), 바비 (마고 로비 주연)" 등에서 → [{title: "듄", keyword: "2021"}, ...]
    entries = [e.strip() for e in raw_result.split(",") if e.strip()]
    parsed = []
    for entry in entries:
        if "(" in entry and ")" in entry:
            title, keyword = entry.split("(", 1)
            parsed.append({"title": title.strip(), "keyword": keyword.strip(" )")})
        else:
            parsed.append({"title": entry.strip(), "keyword": ""})
    return parsed
import os
from dotenv import load_dotenv

import tmdbsimple as tmdb
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationSummaryBufferMemory

from crawler import get_tmdb_overview, get_wikipedia_content, get_watcha_reviews

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
다음 문장에서 영화 제목만 출력하세요. 다른 말은 하지 마세요. 만약 사용자가 물어본 영화 제목이 명확하지 않다면 다시 맞는지 물어보세요.
특히 시리즈물이라면 몇 번 시리즈인지 확실하지 않을 때 사용자에게 명확히 물어보세요.
만일 영화 관련 내용이 아니라면 '없음'이라고 답변하세요.
각 영화 제목은 , 로 구분하세요.

문장: {user_input}
영화 제목:
""")
title_chain = title_extract_prompt | llm

response_prompt = PromptTemplate.from_template("""
아래의 영화 정보와 리뷰들을 참고해 사용자 질문에 답하세요.
리뷰에 포함된 다양한 관점을 반영해 **토론하듯 풍부하게 설명**하세요.
리뷰의 내용을 가져올 때는 왓챠피디아에서 가져온 내용이라는 것을 명시해주세요.
질문이 아니면 자연스럽게 대화를 이어가세요.
영화 추천이 질문으로 들어오면 이전 대화기록과 리뷰를 바탕으로 사용자가 본 적이 없는 비슷한 영화들을 추천해주세요.
추천할 영화 리스트는 "[영화 추천 리스트] 영화제목1, 영화제목2, 영화제목3 ..."의 형식으로 대화의 맨 앞에 표시한 후 대화를 이어가 주세요. 

{context}

질문: {question}
답변:
""")

# --------------------- [3] LLM 도우미 함수 ---------------------
def extract_titles_with_llm(user_input: str) -> list[str]:
    response = title_chain.invoke({"user_input": user_input})
    raw_result = response.content.strip().strip('"').replace("\n", "")

    if not raw_result or raw_result.lower() in {"없음", "해당 없음", "모름", "잘 모르겠음", "영화 아님"} or raw_result.startswith("죄송하지만"):
        return []

    titles = [t.strip() for t in raw_result.split(",") if t.strip()]
    return titles

# --------------------- [4] Chroma 데이터 로딩 ---------------------
def load_data(titles, db):
    for movie_name in titles:
        try:
            existing_titles = {doc.metadata['title'] for doc in db.similarity_search("영화", k=50)}
        except:
            existing_titles = set()

        if movie_name in existing_titles:
            print(f"[스킵됨] '{movie_name}'은 이미 Chroma에 저장되어 있습니다.")
            return

        print(f"[저장됨] '{movie_name}'에 대해 새로 검색합니다.")

        overview = get_tmdb_overview(movie_name)
        wiki = get_wikipedia_content(movie_name) or get_wikipedia_content(movie_name + " (영화)")
        reviews = get_watcha_reviews(movie_name, max_comments=20)
        joined_reviews = "\n\n".join(f"- {r}" for r in reviews)

        combined = f"[영화 제목] {movie_name}\n\n[TMDB 줄거리]\n{overview}\n\n[Wikipedia 문서]\n{wiki}\n\n[왓챠 리뷰]\n{joined_reviews}"
        doc = Document(page_content=combined, metadata={"title": movie_name})

        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents([doc])
        db.add_documents(split_docs)

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

        movie_names = extract_titles_with_llm(user_input)
        if movie_names:
            chroma = get_chroma_shared()
            load_data(movie_names, chroma)
        else:
            print("[안내] 영화 data loading 생략.")

        db = get_chroma_shared()
        memory = get_memory(session_id)

        search_kwargs = {"k": 10}
        if movie_names:
            search_kwargs["filter"] = {"title": {"$in": movie_names}}
        retriever = db.as_retriever(search_kwargs=search_kwargs)

        docs = retriever.get_relevant_documents(user_input)
        context = "\n\n".join([doc.page_content for doc in docs])

        full_prompt = response_prompt.format(context=context, question=user_input)

        print("\n[답변] ", end="", flush=True)
        for token in stream_chat_response(full_prompt):
            print(token, end="", flush=True)
        print()

        '''
        memory.save_context({"input": user_input}, {"output": ""})
        '''
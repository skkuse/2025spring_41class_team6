import os
import tmdbsimple as tmdb
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from typing import Iterator
from crawler import get_tmdb_overview, get_wikipedia_content

tmdb.API_KEY = os.environ.get("TMDB_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY") # 캐릭터 프롬프트 생성용
openrouter_key = os.environ.get("OPEN_ROUTER_KEY") # 대화용

embedding = OpenAIEmbeddings(openai_api_key=openai_key)

# 캐릭터 프롬프트 생성용
llm_openai = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    openai_api_key=openai_key
)

# 챗봇 대화용 LLM
llm_router = ChatOpenAI(
    model="google/gemini-2.5-pro-preview",
    temperature=0.7,
    openai_api_key=openrouter_key,
    openai_api_base="https://openrouter.ai/api/v1",
    streaming=True
)

character_prompt_template = PromptTemplate.from_template("""
주어진 영화 캐릭터 {name}에 대한 정보({context})를 바탕으로, 다음 지침에 따라 캐릭터의 핵심을 파악하고 프롬프트를 생성해주세요.

1.  캐릭터 분석 및 요약:
    * 성격: {name}의 가장 두드러진 성격적 특성(들)은 무엇이며, 이러한 성격이 행동이나 결정에 어떻게 반영되나요? (예: 용감하지만 무모함, 냉소적이지만 속정이 깊음, 계산적이고 치밀함 등)
    * 말투 및 언어적 특징: {name}은 어떤 말투(예: 격식체/비격식체, 직설적/우회적, 특정 어휘 반복, 유머 구사, 사투리나 외국어 섞어 쓰기 등)를 사용하나요?
    * 세계관 및 가치관: {name}이 처한 세계(시대, 장소, 사회적 배경 등)는 그의 가치관, 신념, 목표에 어떤 영향을 미치나요?
    위 분석 내용을 종합하여 {name}의 성격, 말투, 세계관이 명확히 드러나도록 5-8문장으로 요약해주세요.

2.  대화 예시 생성 (2개):
    * 앞서 분석한 {name}의 성격과 말투가 생생하게 드러나는 **대화 예시 3개**를 작성해주세요.
    * 각 대화는 캐릭터가 실제로 할 법한 짧고 임팩트 있는 대사여야 하며, 가능하다면 서로 다른 상황이나 감정을 보여주는 것이 좋습니다.

3.  종합 및 형식:
    * 위 요약과 대화 예시를 합쳐 **총 10문장 이내**로 완성해야 합니다.
    * {name}의 말투가 요약문과 대화 예시 전체에 걸쳐 **매우 명확하고 일관되게** 반영되어야 합니다. 특히 대화 예시는 실제 그 캐릭터가 말하는 것처럼 느껴져야 합니다.

{context}

이제 위 지침에 따라 {name}의 캐릭터 프롬프트를 작성해주세요.

출력 형식:
[캐릭터 프롬프트]
(여기에 생성된 요약 및 대화 예시를 넣어주세요)
""")
character_prompt_chain = LLMChain(prompt=character_prompt_template, llm=llm_openai)

_cached_chroma = None
session_memories = {}
session_prompts = {}

def get_chroma_shared():
    global _cached_chroma
    if _cached_chroma is None:
        os.makedirs("./chroma_data/chracter", exist_ok=True)
        _cached_chroma = Chroma(
            persist_directory="./chroma_data/chracter",
            embedding_function=embedding
        )
    return _cached_chroma

def load_data(movie_name, db):
    try:
        existing_titles = {doc.metadata['title'] for doc in db.similarity_search("영화", k=50)}
    except:
        existing_titles = set()
    if movie_name in existing_titles:
        return
    overview = get_tmdb_overview(movie_name)
    wiki = get_wikipedia_content(movie_name) or get_wikipedia_content(movie_name + " (영화)")
    combined = f"[영화 제목] {movie_name}\n\n[TMDB 줄거리]\n{overview}\n\n[Wikipedia 문서]\n{wiki}"
    docs = [Document(page_content=combined, metadata={"title": movie_name})]
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    db.add_documents(split_docs)

def get_memory(session_id):
    if session_id not in session_memories:
        session_memories[session_id] = ConversationSummaryBufferMemory(
            llm=llm_openai,
            return_messages=True,
            max_token_limit=1000
        )
    return session_memories[session_id]

def stream_chat_response(prompt_text: str) -> Iterator[str]:
    for chunk in llm_router.stream(prompt_text):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content

def get_qa_chain_prompt(session_id: str):
    character_prompt = session_prompts.get(session_id, "")
    full_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
당신은 다음과 같은 인격과 말투를 가진 캐릭터로 응답합니다:

{character_prompt}

캐릭터의 말투와 성격, 세계관을 유지하며 답변해야 합니다.
반드시 캐릭터의 어투, 말끝, 말버릇 등을 반영하고 감정 표현도 포함하세요.
"""),
        ("system", "{history}"),
        ("user", "{question}")
        
    ])
    return full_prompt

# --------- 메인 루프 (스트리밍 출력) --------------
def run_character_mode():
    session_id = "session456"
    db = get_chroma_shared()

    print("캐릭터를 생성할 영화와 등장인물을 입력해주세요.")
    movie = input("영화 제목: ").strip()
    character = input("등장인물 이름: ").strip()
    name = f"{movie} - {character}"

    load_data(movie, db)
    docs = db.similarity_search(movie, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt_result = character_prompt_chain.invoke({"name": character, "context": context})
    character_prompt = prompt_result['text'].strip()
    session_prompts[session_id] = character_prompt
    print("\n[캐릭터 프롬프트]\n" + character_prompt)

    prompt_template = get_qa_chain_prompt(session_id)

    while True:
        user_input = input("\n입력 (종료하려면 'exit'): ")
        if user_input.lower() == "exit":
            break
        
        memory = get_memory(session_id)
        summary = memory.buffer or "(요약 없음)"
        full_prompt = prompt_template.format(history=summary, question=user_input)
        
        print("\n[답변] ", end="", flush=True)
        full_answer = ""
        for token in stream_chat_response(full_prompt):
            print(token, end="", flush=True)
            full_answer += token
        print()
        memory.save_context({"input": user_input}, {"output": full_answer})

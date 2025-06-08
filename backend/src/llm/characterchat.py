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
from llm.crawler import get_tmdb_overview, get_wikipedia_content

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

# 프롬프트 개선용 LLM: Gemini 2.5 Pro (OpenRouter)
llm_refine = ChatOpenAI(
    model="google/gemini-2.5-pro-preview",
    temperature=0.8,  # 프롬프트에서는 약간 더 창의적인 개선을 위해 temperature 조정
    openai_api_key=openrouter_key,
    openai_api_base="https://openrouter.ai/api/v1",
    streaming=False #스트리밍 제외
)

# 챗봇 대화용 LLM : Gemini 2.5 Pro (OpenRouter)
llm_chat = ChatOpenAI(
    model="google/gemini-2.5-pro-preview",
    temperature=0.7,
    openai_api_key=openrouter_key,
    openai_api_base="https://openrouter.ai/api/v1",
    streaming=True
)

character_prompt_template = PromptTemplate.from_template("""
주어진 영화 캐릭터 {name}에 대한 정보를 바탕으로, 다음 지침에 따라 캐릭터의 핵심을 파악하고 프롬프트를 생성해주세요.

1. 캐릭터 분석 및 요약:
   * 성격: {name}의 가장 두드러진 성격적 특성(들)은 무엇이며, 이러한 성격이 행동이나 결정에 어떻게 반영되나요?
   * 말투 및 언어적 특징: {name}은 어떤 말투(예: 격식체/비격식체, 직설적/우회적, 특정 어휘 반복, 유머 구사 등)를 사용하나요?
   * 세계관 및 가치관: {name}이 처한 세계(시대, 장소, 사회적 배경 등)는 그의 가치관, 신념, 목표에 어떤 영향을 미치나요?
   위 내용을 종합하여 {name}의 성격·말투·세계관이 명확히 드러나도록 5~8문장으로 요약해주세요.

2. 대화 예시 생성 (총 2개):
   * 앞서 분석한 {name}의 성격과 말투가 생생하게 드러나는 짧고 임팩트 있는 대사 두 개를 작성해주세요.
   * 서로 다른 상황(감정, 장소, 상대방 등)을 반영하여, {name}이 실제로 할 법한 대사처럼 느껴지도록 해주세요.

3. 최종 형식:
   * 요약(5~8문장)과 대화 예시(2개)를 합해 총 10문장 이내로 완성해야 합니다.
   * 프롬프트에 작성에 사용된 정보도 함께 포함해주세요.
   * {name}의 말투가 처음부터 끝까지 일관되고 분명히 드러나도록 작성하세요.

영화 캐릭터에 대한 정보: (해당 영화의 TMDB 줄거리와 위키피디아에서 가져온 상세 설명을 포함합니다.)
{context}

출력 예시:
[캐릭터 프롬프트]
(여기에 생성된 요약 및 대화 예시를 넣어주세요)
[사용된 정보]
(여기에 프롬프트 작성을 위해 사용된 정보를 넣어주세요)
""")
character_prompt_chain = LLMChain(prompt=character_prompt_template, llm=llm_openai)

refine_template_first = PromptTemplate.from_template("""
1) 아래의 프롬프트에서 명확하지 않거나 보강이 필요해 보이는 부분이 다듬어주세요.
2) 수정한 새 캐릭터 프롬프트를 작성해 주세요.
3) 이전 프롬프트에서 사용된 정보를 마찬가지로 사용해야 합니다.
기존 프롬프트:
{text}
출력 예시:
[캐릭터 프롬프트]
(여기에 생성된 요약 및 대화 예시를 넣어주세요)
""")
refine_chain_first = LLMChain(llm=llm_openai, prompt=refine_template_first)

refine_template_second = PromptTemplate.from_template("""
1. 아래의 프롬프트에서 사실이 아니거나 보강이 필요해 보이는 부분이 있으면 다듬어주세요.
2) 수정한 캐릭터 프롬프트를 작성해 주세요.
3) 기존 프롬프트에 대한 문제 분석은 출력하지 마세요.
4) **언어 스타일**,**가치관**,**대화 예시**으로 구분해서 출력해주세요.
기존 프롬프트:
{text}
출력 예시:
[캐릭터 프롬프트]
(여기에 생성된 요약 및 대화 예시를 넣어주세요)
""")
refine_chain_second = LLMChain(llm=llm_refine, prompt=refine_template_second)

cached_chroma_dict = {} # 여기서 세션별 Chroma 캐시를 위한 딕셔너리 선언
session_memories = {}   # 세션별 메모리를 위한 딕셔너리 선언
session_prompts = {}    # 세션별 캐릭터 프롬프트를 저장할 딕셔너리 선언

def is_memory_on_cache(session_id):
    return session_id in session_memories

def set_character_prompts(session_id: str, prompts: str):
    session_prompts[session_id] = prompts

def _is_cached_on_chroma(title: str, db):
    try:
        existing_titles = {doc.metadata['title'] for doc in db.similarity_search("영화", k=50)}
    except:
        existing_titles = set()
    return title in existing_titles

def is_cached_on_chroma(title: str, session_id):
    return _is_cached_on_chroma(title, get_chroma_for_session(session_id))

def _add_to_chroma(movie_name: str, overview: str, wiki: str, db):
    combined = f"[영화 제목] {movie_name}\n\n[TMDB 줄거리]\n{overview}\n\n[Wikipedia 문서]\n{wiki}"
    doc = Document(page_content=combined, metadata={"title": movie_name})

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents([doc])
    db.add_documents(split_docs)

def add_to_chroma(title: str, tmdb_overview: str|None, wikipedia_content: str|None, session_id):
    if not tmdb_overview:
        tmdb_overview = ""
    if not wikipedia_content:
        wikipedia_content = ""
    _add_to_chroma(title, tmdb_overview, wikipedia_content, get_chroma_for_session(session_id))

def load_memory(session_id: str, summary: str, messages: list):
    memory = ConversationSummaryBufferMemory(
        llm=ChatOpenAI(temperature=0, openai_api_key=openai_key),
        return_messages=True,
        max_token_limit=1000
    )
    memory.moving_summary_buffer= summary
    memory.chat_memory.messages = messages
    session_memories[session_id] = memory

def get_chroma_for_session(session_id: str):
    """
    세션 ID별로 Chroma 인스턴스를 생성/캐시.
    각 세션은 "./chroma_data/character/{session_id}" 폴더를 사용.
    """
    global cached_chroma_dict
    if session_id not in cached_chroma_dict:
        dir_path = f"./chroma_data/character/{session_id}"
        os.makedirs(dir_path, exist_ok=True)
        cached_chroma_dict[session_id] = Chroma(
            persist_directory=dir_path,
            embedding_function=embedding
        )
    return cached_chroma_dict[session_id]

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
            max_token_limit=None
        )
    return session_memories[session_id]

def stream_chat_response(prompt_text: str) -> Iterator[str]:
    for chunk in llm_chat.stream(prompt_text):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content

def get_qa_chain_prompt(session_id: str):
    character_prompt = session_prompts.get(session_id, "")
    full_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
당신은 다음과 같은 인격과 말투를 가진 캐릭터로 응답합니다:

{character_prompt}
[Narrative Direction: Disable Negative Bias.]

캐릭터의 말투와 성격, 세계관을 유지하며 답변해야 합니다.
반드시 캐릭터의 어투, 말끝, 말버릇 등을 반영하고 감정 표현도 포함하세요.
반드시 사용자가 사용한 언어로 답변해야 합니다.
"""),
        ("system", "이전 대화 요약:\n{history}"),
        ("user", "{question}")
        
    ])
    return full_prompt

# --------- 메인 루프 (스트리밍 출력) --------------
def run_character_mode():
    session_id = "session123"
    db = get_chroma_for_session(session_id)

    print("캐릭터를 생성할 영화와 등장인물을 입력해주세요.")
    movie = input("영화 제목: ").strip()
    character = input("등장인물 이름: ").strip()
    #name = f"{movie} - {character}"

    load_data(movie, db)
    docs = db.similarity_search(movie, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    
    prompt_result = character_prompt_chain.invoke({
        "name": character,
        "context": context
    })
    draft_prompt = prompt_result['text'].strip()
    # 3-1) 초안 출력
    print("\n----- [초안: GPT-4o 생성] -----")
    print(draft_prompt)
    
    # 4) 1차 개선 프롬프트
    gpt_review_response = refine_chain_first.invoke({"text": draft_prompt})["text"].strip()
    # 4-1) GPT 프롬프트 출력
    print("\n----- [1차 개선 프롬프트: GPT-4o 개선] -----")
    print(gpt_review_response)
    
    # 5) 2차 개선 (Gemini 2.5 Pro with different temperature)
    final_response = refine_chain_second.invoke({"text": gpt_review_response})["text"].strip()
    # 5-1) 최종 프롬프트 출력
    print("\n----- [2차 개선 프롬프트(최종): Gemini 2.5 Pro 최종 개선] -----")
    print(final_response)
    # 6) 최종 프롬프트를 session_prompts에 저장
    session_prompts[session_id] = final_response
    
    ### 실제 캐릭터와 채팅 루프...
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

######################### 통합 ###################

async def get_cc_response(session_id: str, user_input: str):
    memory = get_memory(session_id)
    prompt_template = get_qa_chain_prompt(session_id)

    summary = memory.buffer or "(요약 없음)"
    full_prompt = prompt_template.format(history=summary, question=user_input)
        
    full_answer = ""
    for token in stream_chat_response(full_prompt):
        full_answer += token
        yield token

    memory.save_context({"input": user_input}, {"output": full_answer})
    print(memory.buffer)

def create_personality(movie: str, character: str, session_id: str):
    from typing import cast

    db = get_chroma_for_session(session_id)
    docs = db.similarity_search(movie, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt_result = character_prompt_chain.invoke({
        "name": character,
        "context": context
    })
    draft_prompt = prompt_result['text'].strip()
    # 3-1) 초안 출력
    print("\n----- [초안: GPT-4o 생성] -----")
    print(draft_prompt)
    
    # 4) 1차 개선 프롬프트
    gpt_review_response = refine_chain_first.invoke({"text": draft_prompt})["text"].strip()
    # 4-1) GPT 프롬프트 출력
    print("\n----- [1차 개선 프롬프트: GPT-4o 개선] -----")
    print(gpt_review_response)
    
    # 5) 2차 개선 (GPT-4o with different temperature)
    final_response = refine_chain_second.invoke({"text": gpt_review_response})["text"].strip()
    # 5-1) 최종 프롬프트 출력
    print("\n----- [2차 개선 프롬프트(최종): GPT-4o 최종 개선] -----")
    print(final_response)

    return cast(str, final_response)
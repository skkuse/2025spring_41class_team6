import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableLambda, RunnableMap
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage
from common.env import ENV_OPENAI_API_KEY
from pydantic import SecretStr

assert(ENV_OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=SecretStr(ENV_OPENAI_API_KEY))

# 제목 생성용 프롬프트
title_prompt = PromptTemplate.from_template("""
당신은 AI 비서입니다.
아래는 사용자와 AI의 대화 내역입니다. 이 대화의 주제를 간결하게 요약해 채팅방 제목을 생성하세요.

- 제목은 3~7단어 이내로 작성
- 핵심 주제를 담고, 불필요한 단어는 제거
- 포멀하지 않아도 되고, 자연스러워도 됩니다

대화:
{chat_history}

채팅방 제목:
""")

title_chain = title_prompt | llm

def generate_chat_title(chat_history: str) -> str:
    response = title_chain.invoke({"chat_history": chat_history})
    return response.content.strip()

# ---------------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0)

extract_subject_prompt = PromptTemplate.from_template("""
이전 대화 요약:
{history}

당신은 영화 전문가 AI입니다.
이전의 대화와 지금 사용자의 입력을 기반으로 현재 사용자가 이야기하고 있는 영화와 가장 관련성이 높은 영화 제목과 개봉일을 1에서 3개 정도 추론하세요.
사용자의 주제가 명확하다면 1개만, 불명확하다면 3개까지 추론하세요.
만약 추론할 수 없는 상황이라면, 빈 배열을 출력하세요.

- 특히 시리즈물이라면 몇 번 시리즈인지 숫자를 기반으로 명확히 구분해주세요.
- 개별 영화만 추출하며, 관련 콘텐츠(애니메이션, 단편 등)는 제외합니다.
- 시리즈물이지만 번호나 부제 없이 단일 제목만 있는 경우 시리즈에 대한 질문이라고 가정하고, 시리즈의 대표적인 영화 제목을 최대 3개 추출합니다.

출력 형식은 반드시 다음과 같은 JSON 형식이어야 합니다:
[
{{
  "title": "영화 제목 (예: 듄 2)",
  "series": 2,
  "year": 2024,
  "confidence": 0.9
}},
{{
  "title": "영화 제목2",
  "series": 1,
  "year": 2020,
  "confidence": 0.4
}}
]                                  
title은 영화 제목, year는 개봉 연도, confidence는 명확한 정도입니다. 개봉 연도가 명확하지 않다면 year는 null로 주세요.
만약 시리즈물이라면 영화가 몇 번째 시리즈인지 series에 작성하세요. 만약 시리즈물이 아니라면 1로 작성해주세요.
반드시 confidence가 높은 순으로 출력하세요.
                                                      
현재 사용자 입력: {user_input}
출력:
""")

json_parser = JsonOutputParser()
extract_movie_subject_chain = extract_subject_prompt | llm | json_parser

from pydantic import BaseModel
from typing import Optional, List
class Subject(BaseModel):
    title: Optional[str] = None
    series: int = 1
    year: Optional[int] = None
    confidence: float = 0.0

def get_current_subject(memory_buffer, user_message: str) -> List[Subject]:
    from common.logging_config import logger
    
    try:
        results = extract_movie_subject_chain.invoke({ "history": memory_buffer, "user_input": user_message })
        logger.info(f"subjects: {results}")
        return [Subject(**result) for result in results]
        
    except Exception as e:
        logger.error(e)
        return []

import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
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

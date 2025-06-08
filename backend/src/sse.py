SSE_TYPE = "type"
SSE_CONTENT = "content"


SSE_SIGNAL = "signal"
"""[SSE TYPE] content에 server측에서 client한테 유용할 수도 있는 신호를 담음"""

SSE_RECOMMEND = "recommendation"
"""[SSE TYPE] content에 AI가 추천한 영화 ID가 list[int] 형태로 담김"""

SSE_ROOM_TITLE = "room title"
"""[SSE TYPE] content에 ChatRoom의 변경된 이름이 담겨 있음"""

SSE_MESSAGE = "message"
"""[SSE TYPE] content에 AI가 생성한 응답 token이 담겨 있음"""

SSE_CHATROOM = "created chatroom"
"""[SSE TYPE] content에 생성한 ChatRoom이 dict(CreateChatRoomResponse) 형태로 담겨 있음"""

SSE_CC_START = "cc create start"
"""
[SSE SIGNAL] character 생성 시작 시 발생하는 signal.  
캐릭터가 이미 만들어져 있었다면 오지 않을 수도 있음.
"""

SSE_CC_DONE = "cc create done"
"""
[SSE SIGNAL] character 생성이 성공적으로 완료 시 발생하는 signal.  
캐릭터가 이미 만들어져 있었다면 `SSE_CC_START` 없이 바로 발생함.  
"""

SSE_CC_FAIL = "cc create fail"
"""
[SSE SIGNAL] character 생성 실패 시 발생하는 signal.  
만약 채팅방이 생성되었더라도, 삭제됨.
"""

SSE_CRAWL_START= "crawling start"
"""[SSE SIGNAL] 크롤링 시작 시 발생하는 signal"""

SSE_CRAWL_END = "crawling end"
"""[SSE SIGNAL] 크롤링 종료 시 발생하는 signal"""

SSE_MESSAGE_START = "message start"
"""[SSE SIGNAL] 메시지 시작 시 발생하는 signal"""

SSE_MESSAGE_END = "message end"
"""[SSE SIGNAL] 메시지 종료 시 발생하는 signal"""

SSE_DB_START = "database start"
"""[SSE SIGNAL] DB 연산 시작 시 발생할 수도 있는 signal"""

SSE_DB_END = "database end"
"""[SSE SIGNAL] `SSE_DB_START` signal 이후 DB 연산 종료 시 발생하는 signal"""

SSE_FINISH = "sse finish"
"""[SSE SIGNAL] 요청에 대한 모든 응답을 보냄"""

from typing import Any

def make_sse(type: str, content: Any):
  """
  SSE 메시지 chunk를 생성하는 helper 함수입니다.
  """
  return {
    SSE_TYPE: type,
    SSE_CONTENT: content
  }

def sse_type(data: dict) -> str:
  return data[SSE_TYPE]

def sse_content(data: dict):
  return data[SSE_CONTENT]

def sse_to_string(chunk):
  """
  SSE 메시지 chunk를 직렬화합니다.  
  StreamingResponse에 직접 yield 시 적용하면 됩니다.
  """
  import json
  return f"data: {json.dumps(chunk)}\n\n"

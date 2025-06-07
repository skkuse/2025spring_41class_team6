SSE_SIGNAL = "signal"
SSE_RECOMMEND = "recommendation"
SSE_MESSAGE = "message"

SSE_TYPE = "type"
SSE_CONTENT = "content"

SSE_CRAWL_START= "crawling start"
SSE_CRAWL_END = "crawling end"
SSE_MESSAGE_START = "message start"
SSE_MESSAGE_END = "message end"
SSE_DB_START = "database start"
SSE_DB_END = "database end"
SSE_FINISH = "sse finish"

from typing import Any

def make_sse(type: str, content: Any):
  return {
    SSE_TYPE: type,
    SSE_CONTENT: content
  }

def sse_type(data: dict) -> str:
  return data[SSE_TYPE]

def sse_content(data: dict):
  return data[SSE_CONTENT]

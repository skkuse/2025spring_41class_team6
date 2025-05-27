from datetime import date, datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.utils import *
from database.models import Base, engine, SessionLocal, User

# table 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI() # entry point

class ChatRoomCreate(BaseModel):
  initial_message: str


class MessageRequest(BaseModel):
  content: str

class ChatMessage(BaseModel):
  user_message: str
  ai_message: str
  timestamp: datetime

class ChatRoom(BaseModel):
  id: int
  title: str
  chats: list[ChatMessage]

class MovieData(BaseModel):
  id: int
  title: str
  overview: str|None
  wiki_document: str|None
  release_date: date
  poster_img_url: str|None
  trailer_img_url: str|None
  rating: int
  ordering: int

class _chatresponse(BaseModel):
  text: str

  def getText(self): return self.text

# DB session을 가져옵니다.
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

def _map_to_chat_message(internal_doc) -> ChatMessage:
  return ChatMessage(
    user_message=internal_doc["user_chat"],
    ai_message=internal_doc["ai_chat"],
    timestamp=internal_doc["timestamp"]
  )

def _map_to_movie_data(internal_data) -> MovieData:
  raise NotImplementedError


async def _send_message_to_ai(msg: str, cxt) -> _chatresponse:
  raise NotImplementedError



def getUser(db: Session, email: str, password: str, nickname: str):
  return db_create_new_user(db, email, password, nickname)

@app.get("/")
async def root():
  return {}

@app.post("/chatrooms", response_model=ChatRoom)
async def create_new_chatroom(data: ChatRoomCreate, db: Session = Depends(get_db)):
  user_id = getUser(db, "paul3143@naver.com", "1234", "sk")
  if user_id is None:
    raise HTTPException(status_code=403, detail="Unauthorized")

  res = db_make_new_chatroom(db, user_id)
  if res is None:
    raise HTTPException(status_code=500, detail="채팅방을 만들 수 없었습니다")

  room_id = res["id"]

  ret = ChatRoom(
    id=room_id,
    title=res["title"],
    chats=[]
  )
  try:
    response = await _send_message_to_ai(data.initial_message, None)
    r = db_append_chat_message(db, room_id, data.initial_message, response.getText())
    if r is not None:
      ret.chats = [_map_to_chat_message(r)]
    return ret
  except:
    raise HTTPException(status_code=500, detail="기타 서버 에러")

@app.post("/chatrooms/{room_id}/messages", response_model=ChatMessage)
def send_message(room_id: int, message: MessageRequest, db: Session = Depends(get_db)):
  cxt = db_get_chatroom_context(db, room_id)
  if cxt is None:
    raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

  try:
    response = _send_message_to_ai(message.content, cxt)
  except Exception as e:
    print(f"에러: {e}")
    raise HTTPException(status_code=500, detail="AI 응답 오류")

  db_update_chatroom_context(db, response, cxt)
  return _map_to_chat_message(response)

@app.get("/chatrooms/{room_id}/messages", response_model=list[ChatMessage])
def chatroom_history(room_id: int, db: Session = Depends(get_db)):
  history = db_get_chatroom_history(db, room_id)
  if history is None:
    raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

  return [_map_to_chat_message(i) for i in history]

@app.get("/movies/{id}", response_model=MovieData)
def get_movie_data(id: int, db: Session = Depends(get_db)):
  data = db_find_movie_by_id(db, id)
  if data is None:
    raise HTTPException(status_code=404, detail="영화를 찾을 수 없음")
  return _map_to_movie_data(data)

@app.get("/movies/bookmarked", response_model=list[MovieData])
def get_bookmarked_movies(db: Session = Depends(get_db)):
  data = db_get_bookmarked_movies(db)
  return [_map_to_movie_data(i) for i in data]

@app.post("/movies/bookmarked", response_model=MovieData)
def add_bookmark(id: int, db: Session = Depends(get_db)):
  try:
    data = db_add_bookmark(db, id)
    return _map_to_movie_data(data)
  
  except FileExistsError:
    raise HTTPException(status_code=409, detail="이미 북마크 되었습니다.")
  except FileNotFoundError:
    raise HTTPException(status_code=404, detail="존재하지 않는 영화를 북마크할 수 없습니다.")

@app.post("/movies/bookmarked/{id}", response_model=None)
def rm_bookmark(id: int, db: Session = Depends(get_db)):
  try:
    db_rm_bookmark(db, id)
  except Exception:
    raise HTTPException(status_code=404, detail="북마크 해제 실패")

@app.post("/test/users/")
def create_user(user: str, content: str, db: Session = Depends(get_db)):
  user = User(
    email="test@gmail.com",
    password="test_password",
    nickname="test_nickname"
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

@app.get("/test/users/")
def get_users(db: Session = Depends(get_db)):
  return db.query(User).all()
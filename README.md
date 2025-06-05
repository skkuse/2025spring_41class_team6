# Moviechat README (for dev)
## backend 서버 실행
`.env` 설정 (backend 폴더에 있으면 됨)
```
BACKEND_ROOT=/(절대경로)/2025spring_41class_team6/backend
OPENAI_API_KEY=(...)
TMDB_API_KEY=(...)
```
```bash
cd backend/src # 소스 폴더로 이동
uvicorn main:app --reload # 코드 자동반영이 필요하다면 --reload 옵션 주기
```

## backend API end point
frontend에서 backend로 요청을 보낼 수 있는 API입니다.  
각 endpoint 경로 앞에 `api`을 붙여서 요청해주세요  
예) `api/movies/bookmarked`

## how to test?
uvicorn으로 실행 시, `127.0.0.1:8000/docs` 에서 직접 endpoint에 payload, request등을 보내볼 수 있습니다.

### /chatrooms
#### GET
현재 user session(=cookie)의 채팅방 리스트 반환  
```json
{
    "normal": [
        {
            "id": 1234,
            "title": "채팅방 이름"
        },
        {
            "id": 356,
            "title": "채팅방 #2"
        }
    ],
    "immersive": [
        {
            "id": 534566000,
            "title": "몰입형 대화 #1"
        }
    ]
}
```
#### POST
현재 user에게 채팅방 생성  
initial message로 생성과 동시에 AI에게 질의를 보내줌
* 요청
```json
{
    "initial_message": "최초 사용자 메세지" // optional
}
```
* 응답
```json
{
    "id": 1234,
    "title": "채팅방 이름",
    "chats": [
        { /* chat history #1 */ },
        { /* chat history #2 */ },
        // ...
    ]
}
```
### /chatrooms/{room_id}/messages
#### GET
`room_id`의 채팅방의 모든 메세지 내역을 조회
```json
[
    { /* chat history #1 */ },
    { /* chat history #2 */ },
    // ...
]
```
#### POST
`room_id`의 채팅방에 메세지를 보내고 응답을 받음
query로 `stream=true`로 설정하면 [SSE(Server Sent Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
형식으로 응답함. (하단의 chat history 구조를 따르지 않음)  
[(React 참조)](https://velog.io/@april_5/React-Server-Sent-EventsSSE-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0)
* 요청
```json
{
    "content": "유저 질문"
}
```
* 응답
```json
// chat history 구조
{
    "user_message": "유저 질문",
    "ai_message": "AI 응답",
    "timestamp": "2025-15-06 17:00:00" // datetime
    // 기타 데이터 (ex: 사진)
}
```
* 응답 (stream=true)
```
data: 안

data: 녕

data: 하

data: 세요
```
응답에 timestamp와 user_message가 현재 반환되지 않습니다. client에서 time을 설정해줘도 무방할 것 같긴한데,
혹시 필요하다면 말씀해주세요. (DB에는 정상적으로 timestamp, message가 저장됨)

**아래부터는 아직 구현이 되지 않은, STUB입니다**
(동작은 합니다)  
(몰입형 기능은 merge만 하였고, 아직 내부적으로 따로 처리하진 않은 상태입니다)

### /movies/{id}
#### GET
`id`의 영화 정보를 불러옴 (MovieChat 고유 ID)  
이 end point에서는 `rating`, `ordering`이 `0`으로 고정되어 돌아옴. 무시해도 됨.
```json
// movie data 구조
{
    "id": 23, // MovieChat DB ID
    "title": "영화 제목(TMDB-ko 기준)",
    "overview": "영화 줄거리 요약",
    "wiki_document": "wiki 줄거리",
    "release_date": "2000-00-00 00:00:00",
    "poster_img_url": "https://~~~~~~~",
    "trailer_img_url": "https://~~~~~~~",
    "rating": 0, // 고정 필드(archive된 거라면 이 값이 정수형 0~5)
    "ordering": 0 // 고정 필드(bookmark/archive된 거라면 이 값이 세팅됨; 프론트에서 오름차순으로 정렬해서 보여주면 됨)
}
```

### /movies/bookmarked
#### GET
현재 user session의 북마크된 영화 정보들을 불러옴
```json
[   // ordering이 세팅됨
    { /* movie data #1 */ },
    { /* movie data #2 */ },
    // ...
]
```
#### POST
현재 user session에 영화를 북마크함
* 요청
```json
{
    "id": 23 // MovieChat DB ID
}
```
* 응답
```json
// ordering이 세팅됨
{ /* bookmarked movie data */ }
```

#### DELETE
현재 user session에 bookmark된 영화를 북마크 해제함.
```json
{
    "id": 23 // MovieChat DB ID
}
```
* 응답
```json
// ordering이 세팅됨
{ /* bookmarked movie data */ }
```

### /movies/archive
#### GET
현재 user session의 archive된 영화 정보들을 불러옴
```json
[   // ordering이 세팅됨
    // ranking이 세팅됨
    { /* movie data #1 */ },
    { /* movie data #2 */ },
    // ...
]
```
#### POST
현재 user session에 영화를 북마크함
* 요청
```json
{
    "id": 23, // MovieChat DB ID
    "ranking": 3 // 3점
}
```
* 응답
```json
// ordering이 세팅됨
// ranking이 세팅됨
{ /* archived movie data */ }
```

#### DELETE
현재 user session에 archive된 영화를 북마크 해제함.
```json
{
    "id": 23 // MovieChat DB ID
}
```
* 응답
```json
// ordering이 세팅됨
// ranking이 세팅됨
{ /* archived movie data */ }
```
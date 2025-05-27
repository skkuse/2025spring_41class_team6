# Moviechat README (for dev)
## backend API end point
frontend에서 backend로 요청을 보낼 수 있는 API입니다.  
각 endpoint 경로 앞에 `api`을 붙여서 요청해주세요  
예) `api/movies/bookmarked`
### /
#### GET
특별히 하는 것은 없음.
```json
{ "test": "HTTP 418: I'm a teapot" }
```
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
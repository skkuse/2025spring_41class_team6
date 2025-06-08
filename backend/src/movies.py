from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, Request, status
from api_schema import *
from database.utils import *
from auth import validate_user
from sse import *
import auth

router = APIRouter(prefix="/api/movies", tags=["movie"])

@router.get("/bookmarked", response_model=List[Movie])
async def get_bookmarked(user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    movies = db_get_bookmarked_movies(db, user.id)
    return [public_movie_info(movie) for movie in movies]

@router.post("/bookmarked", response_model=Movie)
async def post_bookmark(payload: MovieIDRequest, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    if db_add_bookmark(db, user.id, payload.id):
        return public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.id, True, user.id) )
        )
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@router.delete("/bookmarked", response_model=Movie)
async def delete_bookmark(payload: MovieIDRequest, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    movie = db_find_movie_by_id(db, payload.id, True, user.id)

    if movie and db_rm_bookmark(db, user.id, payload.id):
        return public_movie_info(movie)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")

# ---------------------------
# /movies/archive
# ---------------------------
@router.get("/archive", response_model=List[Movie])
async def get_archive(user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    movies = db_get_archived_movies(db, user.id)
    return [public_movie_info(movie) for movie in movies]


@router.post("/archive", response_model=Movie)
async def post_archive(payload: ArchiveRequest, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    if db_add_archived(db, user.id, payload.movie_id, payload.rating):
        ret = public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.movie_id, True, user.id) )
        )
        ret.rating = min(5, max(0, payload.rating))
        return ret
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@router.put("/archive", response_model=Movie)
async def update_archive(payload: ArchiveRequest, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    if db_update_archived(db, user.id, payload.movie_id, payload.rating):
        ret = public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.movie_id, True, user.id) )
        )
        ret.rating = min(5, max(0, payload.rating))
        return ret
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@router.delete("/archive", response_model=Movie)
async def delete_archive(payload: MovieIDRequest, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    movie = db_find_movie_by_id(db, payload.id, True, user.id)
    if movie and db_rm_archived(db, user.id, payload.id):
        return public_movie_info(movie)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")

# ---------------------------
# /movies/watchlist
# ---------------------------
@router.get("/watchlist", response_model=List[Movie])
async def get_user_watchlist(user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    try:
        movies = db_get_watchlist(db, user.id)
        return [public_movie_info(movie) for movie in movies]
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

# ---------------------------
# /movies/{id}
# ---------------------------
@router.get("/{id}", response_model=Movie)
async def get_movie(request: Request, id: int = Path(...), verbose: bool = Query(True), db: Session = Depends(get_db)):
    user_id = auth.check_user_id(request)
    movie = db_find_movie_by_id(db, id, verbose, user_id)
    if movie is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="영화가 없습니다.")

    return public_movie_info(movie)

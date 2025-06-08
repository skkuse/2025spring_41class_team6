from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import auth
import chatrooms
import movies

app = FastAPI()

app.include_router(auth.router)
app.include_router(chatrooms.router)
app.include_router(movies.router)

@app.get("/api/user")
async def get_user_information_redirected():
    """호환성을 위한 end point"""
    return RedirectResponse(url="/api/auth/user")
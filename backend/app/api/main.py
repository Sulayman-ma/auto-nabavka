from fastapi import APIRouter

from app.api.routes import bot, login, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(bot.router, tags=["bot"])

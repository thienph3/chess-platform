from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.core.rate_limit import RateLimitMiddleware
from app.modules.achievements.router import router as achievements_router
from app.modules.attendance.router import router as attendance_router
from app.modules.auth.router import router as auth_router
from app.modules.finance.finance_router import finance_router
from app.modules.finance.router import router as transactions_router
from app.modules.games.ai_router import router as ai_router
from app.modules.games.challenge_router import router as challenge_router
from app.modules.games.matchmaking_router import router as matchmaking_router
from app.modules.games.opening_router import router as opening_router
from app.modules.games.router import router as games_router
from app.modules.games.websocket import ws_router
from app.modules.gallery.router import router as gallery_router
from app.modules.members.router import router as members_router
from app.modules.news.router import router as news_router
from app.modules.notifications.router import router as notifications_router
from app.modules.ratings.router import leaderboard_router, router as ratings_router
from app.modules.seasons.router import router as seasons_router
from app.modules.tournaments.match_router import router as match_router
from app.modules.tournaments.router import router as tournaments_router

app = FastAPI(title=settings.APP_NAME, docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting disabled for dev — enable in production
# app.add_middleware(
#     RateLimitMiddleware,
#     rate_limits={
#         "/api/v1/auth/login": (5, 60),
#         "/api/v1/auth/register": (3, 60),
#         "/api/v1/auth/forgot-password": (3, 300),
#     },
# )
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(members_router, prefix=settings.API_V1_PREFIX)
app.include_router(tournaments_router, prefix=settings.API_V1_PREFIX)
app.include_router(match_router, prefix=settings.API_V1_PREFIX)
app.include_router(ratings_router, prefix=settings.API_V1_PREFIX)
app.include_router(leaderboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(transactions_router, prefix=settings.API_V1_PREFIX)
app.include_router(finance_router, prefix=settings.API_V1_PREFIX)
app.include_router(games_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
app.include_router(matchmaking_router, prefix=settings.API_V1_PREFIX)
app.include_router(opening_router, prefix=settings.API_V1_PREFIX)
app.include_router(challenge_router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX)
app.include_router(news_router, prefix=settings.API_V1_PREFIX)
app.include_router(seasons_router, prefix=settings.API_V1_PREFIX)
app.include_router(attendance_router, prefix=settings.API_V1_PREFIX)
app.include_router(achievements_router, prefix=settings.API_V1_PREFIX)
app.include_router(gallery_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)

# Serve uploaded files (avatars, etc.)
import os
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

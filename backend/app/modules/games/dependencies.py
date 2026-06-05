from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.games.repository import GameRepository
from app.modules.games.service import GameService


def get_game_repository(db: AsyncSession = Depends(get_db)) -> GameRepository:
    return GameRepository(db)


def get_game_service(repo: GameRepository = Depends(get_game_repository)) -> GameService:
    return GameService(repo)

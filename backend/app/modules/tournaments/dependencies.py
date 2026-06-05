from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.tournaments.repository import TournamentRepository
from app.modules.tournaments.service import TournamentService


def get_tournament_repository(db: AsyncSession = Depends(get_db)) -> TournamentRepository:
    return TournamentRepository(db)


def get_tournament_service(
    repo: TournamentRepository = Depends(get_tournament_repository),
) -> TournamentService:
    return TournamentService(repo)

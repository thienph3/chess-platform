import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tournaments.models import (
    Match,
    Tournament,
    TournamentParticipant,
    TournamentRound,
    TournamentStatus,
    GameType,
)


class TournamentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: TournamentStatus | None = None,
        game_type: GameType | None = None,
    ) -> tuple[list[Tournament], int]:
        offset = (page - 1) * page_size
        query = select(Tournament).where(Tournament.is_deleted.is_(False))
        count_query = select(func.count()).select_from(Tournament).where(Tournament.is_deleted.is_(False))

        if status:
            query = query.where(Tournament.status == status)
            count_query = count_query.where(Tournament.status == status)
        if game_type:
            query = query.where(Tournament.game_type == game_type)
            count_query = count_query.where(Tournament.game_type == game_type)

        query = query.order_by(Tournament.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        tournaments = list(result.scalars().all())

        total = (await self.db.execute(count_query)).scalar() or 0
        return tournaments, total

    async def get_by_id(self, tournament_id: uuid.UUID) -> Tournament | None:
        query = select(Tournament).where(Tournament.id == tournament_id, Tournament.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, tournament: Tournament) -> Tournament:
        self.db.add(tournament)
        await self.db.commit()
        await self.db.refresh(tournament)
        return tournament

    async def update(self, tournament: Tournament) -> Tournament:
        await self.db.commit()
        await self.db.refresh(tournament)
        return tournament

    async def soft_delete(self, tournament: Tournament) -> None:
        tournament.is_deleted = True
        await self.db.commit()

    # --- Participants ---

    async def add_participant(self, participant: TournamentParticipant) -> TournamentParticipant:
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        return participant

    async def get_participants(self, tournament_id: uuid.UUID) -> list[TournamentParticipant]:
        query = (
            select(TournamentParticipant)
            .where(
                TournamentParticipant.tournament_id == tournament_id,
                TournamentParticipant.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # --- Rounds ---

    async def create_round(self, round_: TournamentRound) -> TournamentRound:
        self.db.add(round_)
        await self.db.commit()
        await self.db.refresh(round_)
        return round_

    async def get_rounds(self, tournament_id: uuid.UUID) -> list[TournamentRound]:
        query = (
            select(TournamentRound)
            .options(selectinload(TournamentRound.matches))
            .where(
                TournamentRound.tournament_id == tournament_id,
                TournamentRound.is_deleted.is_(False),
            )
            .order_by(TournamentRound.round_number)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # --- Matches ---

    async def get_match_by_id(self, match_id: uuid.UUID) -> Match | None:
        query = select(Match).where(Match.id == match_id, Match.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_match(self, match: Match) -> Match:
        await self.db.commit()
        await self.db.refresh(match)
        return match

    async def create_match(self, match: Match) -> Match:
        self.db.add(match)
        await self.db.flush()
        return match

    async def get_all_matches(self, tournament_id: uuid.UUID) -> list[Match]:
        """Lấy tất cả ván đấu của một giải đấu (qua rounds)."""
        query = (
            select(Match)
            .join(TournamentRound, Match.round_id == TournamentRound.id)
            .where(
                TournamentRound.tournament_id == tournament_id,
                TournamentRound.is_deleted.is_(False),
                Match.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def commit(self) -> None:
        await self.db.commit()

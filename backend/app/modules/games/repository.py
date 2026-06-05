import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.games.models import GameRoom, GameRoomStatus, MoveHistory


class GameRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_room(self, room: GameRoom) -> GameRoom:
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_room_by_id(self, room_id: uuid.UUID) -> GameRoom | None:
        query = select(GameRoom).where(GameRoom.id == room_id, GameRoom.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_live_rooms(self) -> list[GameRoom]:
        query = (
            select(GameRoom)
            .where(GameRoom.status.in_([GameRoomStatus.waiting, GameRoomStatus.playing]))
            .where(GameRoom.is_deleted.is_(False))
            .order_by(GameRoom.created_at.desc())
            .limit(50)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_room(self, room: GameRoom) -> GameRoom:
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def add_move(self, move: MoveHistory) -> MoveHistory:
        self.db.add(move)
        await self.db.commit()
        await self.db.refresh(move)
        return move

    async def get_moves(self, room_id: uuid.UUID) -> list[MoveHistory]:
        query = (
            select(MoveHistory)
            .where(MoveHistory.room_id == room_id)
            .order_by(MoveHistory.move_number)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_finished_rooms(self, limit: int = 50) -> list[GameRoom]:
        query = (
            select(GameRoom)
            .where(GameRoom.status == GameRoomStatus.finished, GameRoom.is_deleted.is_(False))
            .order_by(GameRoom.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

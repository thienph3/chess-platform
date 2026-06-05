"""Add game tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("white_player_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("black_player_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=True),
        sa.Column("status", sa.Enum("waiting", "playing", "finished", "aborted", name="gameroomstatus"), default="waiting"),
        sa.Column("game_type", sa.String(20), nullable=False),
        sa.Column("time_control", sa.Integer, default=300),
        sa.Column("fen", sa.Text, nullable=True),
        sa.Column("result", sa.String(20), nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "move_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", UUID(as_uuid=True), sa.ForeignKey("game_rooms.id"), nullable=False),
        sa.Column("move_number", sa.Integer, nullable=False),
        sa.Column("notation", sa.String(20), nullable=False),
        sa.Column("fen_after", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("move_history")
    op.drop_table("game_rooms")
    op.execute("DROP TYPE IF EXISTS gameroomstatus")

"""Add tournament mode and round start_time.

Revision ID: 005
Revises: 004
"""
import sqlalchemy as sa

from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tournament mode: online or otb
    op.execute("CREATE TYPE tournamentmode AS ENUM ('online', 'otb')")
    op.add_column("tournaments", sa.Column("mode", sa.Enum("online", "otb", name="tournamentmode"), server_default="online", nullable=False))

    # Round start_time (for online tournaments)
    op.add_column("tournament_rounds", sa.Column("start_time", sa.DateTime(timezone=True), nullable=True))

    # Game room scheduled_start
    op.add_column("game_rooms", sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True))

    # Move history review data
    op.add_column("move_history", sa.Column("classification", sa.String(20), nullable=True))
    op.add_column("move_history", sa.Column("eval_after", sa.Integer, nullable=True))
    op.add_column("move_history", sa.Column("best_move", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("move_history", "best_move")
    op.drop_column("move_history", "eval_after")
    op.drop_column("move_history", "classification")
    op.drop_column("game_rooms", "scheduled_start")
    op.drop_column("tournament_rounds", "start_time")
    op.drop_column("tournaments", "mode")
    op.execute("DROP TYPE IF EXISTS tournamentmode")

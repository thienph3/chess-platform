"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Members
    op.create_table(
        "members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("skill_level", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tournaments
    op.create_table(
        "tournaments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("game_type", sa.Enum("chess", "xiangqi", "go", name="gametype"), nullable=False),
        sa.Column("time_format", sa.Enum("bullet", "blitz", "rapid", "standard", name="timeformat"), nullable=False),
        sa.Column("format", sa.Enum("round_robin", "swiss", "knockout", name="tournamentformat"), nullable=False),
        sa.Column("max_participants", sa.Integer, nullable=False),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "registration", "in_progress", "completed", "cancelled", name="tournamentstatus"),
            default="draft",
        ),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tournament Participants
    op.create_table(
        "tournament_participants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tournament_id", UUID(as_uuid=True), sa.ForeignKey("tournaments.id"), nullable=False),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("registered", "confirmed", "withdrawn", name="participantstatus"),
            default="registered",
        ),
        sa.Column("seed", sa.Integer, nullable=True),
        sa.Column("final_rank", sa.Integer, nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tournament Rounds
    op.create_table(
        "tournament_rounds",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tournament_id", UUID(as_uuid=True), sa.ForeignKey("tournaments.id"), nullable=False),
        sa.Column("round_number", sa.Integer, nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", name="roundstatus"),
            default="pending",
        ),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Matches
    op.create_table(
        "matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("round_id", UUID(as_uuid=True), sa.ForeignKey("tournament_rounds.id"), nullable=False),
        sa.Column("white_player_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("black_player_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column(
            "result",
            sa.Enum("white_win", "black_win", "draw", "pending", name="matchresult"),
            default="pending",
        ),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Ratings
    op.create_table(
        "ratings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("game_type", sa.Enum("chess", "xiangqi", "go", name="gametype", create_type=False), nullable=False),
        sa.Column("time_format", sa.Enum("bullet", "blitz", "rapid", "standard", name="timeformat", create_type=False), nullable=False),
        sa.Column("rating", sa.Integer, default=1200),
        sa.Column("games_played", sa.Integer, default=0),
        sa.Column("wins", sa.Integer, default=0),
        sa.Column("draws", sa.Integer, default=0),
        sa.Column("losses", sa.Integer, default=0),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("member_id", "game_type", "time_format", name="uq_rating_member_game_time"),
    )

    # Rating Changes
    op.create_table(
        "rating_changes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("rating_id", UUID(as_uuid=True), sa.ForeignKey("ratings.id"), nullable=False),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("old_rating", sa.Integer, nullable=False),
        sa.Column("new_rating", sa.Integer, nullable=False),
        sa.Column("change", sa.Integer, nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Transactions
    op.create_table(
        "transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.Enum("income", "expense", name="transactiontype"), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "membership_fee", "sponsorship", "donation", "other_income",
                "venue", "prize", "equipment", "food", "other_expense",
                name="transactioncategory",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=True),
        sa.Column("tournament_id", UUID(as_uuid=True), sa.ForeignKey("tournaments.id"), nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("rating_changes")
    op.drop_table("ratings")
    op.drop_table("transactions")
    op.drop_table("matches")
    op.drop_table("tournament_rounds")
    op.drop_table("tournament_participants")
    op.drop_table("tournaments")
    op.drop_table("members")
    op.execute("DROP TYPE IF EXISTS gametype")
    op.execute("DROP TYPE IF EXISTS timeformat")
    op.execute("DROP TYPE IF EXISTS tournamentformat")
    op.execute("DROP TYPE IF EXISTS tournamentstatus")
    op.execute("DROP TYPE IF EXISTS participantstatus")
    op.execute("DROP TYPE IF EXISTS roundstatus")
    op.execute("DROP TYPE IF EXISTS matchresult")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS transactioncategory")

"""Add all missing tables and columns.

Revision ID: 004
Revises: 003
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("type", sa.Enum("tournament_invite", "match_result", "game_invite", "system", name="notificationtype")),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- news_posts ---
    op.create_table(
        "news_posts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_pinned", sa.Boolean, default=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- attendance ---
    op.create_table(
        "attendance",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("event_type", sa.Enum("regular", "tournament", "special", name="eventtype"), default="regular"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- seasons ---
    op.create_table(
        "seasons",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("game_type", sa.String(20), nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- achievements ---
    op.create_table(
        "achievements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("icon", sa.String(50), default="emoji_events"),
        sa.Column("condition_type", sa.String(50), nullable=False),
        sa.Column("condition_value", sa.Integer, nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- member_achievements ---
    op.create_table(
        "member_achievements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("achievement_id", UUID(as_uuid=True), sa.ForeignKey("achievements.id"), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- gallery_images ---
    op.create_table(
        "gallery_images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("tournament_id", UUID(as_uuid=True), sa.ForeignKey("tournaments.id"), nullable=True),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=True),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- challenges ---
    op.create_table(
        "challenges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("challenger_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("challenged_id", UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("game_type", sa.String(20), nullable=False),
        sa.Column("time_control", sa.Integer, default=300),
        sa.Column("status", sa.Enum("pending", "accepted", "declined", "expired", name="challengestatus"), default="pending"),
        sa.Column("is_deleted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Missing columns ---
    op.add_column("members", sa.Column("avatar_url", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("reset_token", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("reset_token_expires", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tournaments", sa.Column("spectator_delay", sa.Integer, server_default="0", nullable=False))
    op.add_column("tournaments", sa.Column("prizes_json", sa.JSON, nullable=True))
    op.add_column("game_rooms", sa.Column("increment", sa.Integer, server_default="0", nullable=False))
    op.add_column("game_rooms", sa.Column("white_accuracy", sa.Float, nullable=True))
    op.add_column("game_rooms", sa.Column("black_accuracy", sa.Float, nullable=True))
    op.add_column("game_rooms", sa.Column("is_reviewed", sa.Boolean, server_default="false", nullable=False))

    # Seed: AI player member record
    op.execute(
        "INSERT INTO members (id, full_name, email, is_deleted, created_at, updated_at) "
        "VALUES ('00000000-0000-0000-0000-000000000001', 'VCC Bot', 'ai@vcc.local', false, now(), now()) "
        "ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_column("game_rooms", "is_reviewed")
    op.drop_column("game_rooms", "black_accuracy")
    op.drop_column("game_rooms", "white_accuracy")
    op.drop_column("game_rooms", "increment")
    op.drop_column("tournaments", "prizes_json")
    op.drop_column("tournaments", "spectator_delay")
    op.drop_column("users", "reset_token_expires")
    op.drop_column("users", "reset_token")
    op.drop_column("members", "avatar_url")
    op.drop_table("challenges")
    op.drop_table("gallery_images")
    op.drop_table("member_achievements")
    op.drop_table("achievements")
    op.drop_table("seasons")
    op.drop_table("attendance")
    op.drop_table("news_posts")
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS challengestatus")
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS eventtype")

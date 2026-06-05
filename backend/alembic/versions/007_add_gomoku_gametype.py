"""Add gomoku to gametype enum.

Revision ID: 007
Revises: 006
"""
from alembic import op

revision = "007"
down_revision = "006"


def upgrade() -> None:
    op.execute("ALTER TYPE gametype ADD VALUE IF NOT EXISTS 'gomoku'")


def downgrade() -> None:
    # PostgreSQL không hỗ trợ xóa value khỏi enum một cách đơn giản.
    # Cần recreate type nếu muốn rollback.
    pass

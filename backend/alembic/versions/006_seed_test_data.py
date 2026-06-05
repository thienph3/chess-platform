"""Seed test data: user phthien + sample game.

Revision ID: 006
Revises: 005
"""
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None

MEMBER_ID = "c4e96e0e-4616-4358-8ee4-4342fb96f341"
USER_ID = "c4e96e0e-4616-4358-8ee4-4342fb96f341"
AI_MEMBER_ID = "00000000-0000-0000-0000-000000000001"
GAME_ROOM_ID = "f9d42bd9-0a06-4698-875b-8bd1e53a3768"

MOVES = [
    "e2e4", "c7c5", "g1f3", "g7g6", "d2d4", "c5d4", "d1d4", "g8f6",
    "e4e5", "b8c6", "d4h4", "f6d5", "f1c4", "d5b6", "c4b3", "f8g7",
    "c1h6", "e8g8", "b1c3", "d7d5", "e1c1", "e7e6", "f3g5", "f7f6",
    "e5f6", "g7f6", "h1e1", "f8e8", "c3e4", "f6h8", "d1d3", "c6e5",
    "d3d1", "b6c4", "f2f4",
]


def upgrade() -> None:
    import bcrypt
    hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8")

    # Use raw SQL with inline UUID casts to avoid SQLAlchemy bind param issues
    op.execute(
        f"INSERT INTO members (id, full_name, email, is_deleted, created_at, updated_at) "
        f"VALUES ('{MEMBER_ID}'::uuid, 'Phan Huu Thien', 'phthien@vinamilk.com.vn', false, now(), now()) "
        f"ON CONFLICT (id) DO NOTHING"
    )

    op.execute(
        f"INSERT INTO users (id, email, hashed_password, role, member_id, is_active, is_deleted, created_at, updated_at) "
        f"VALUES ('{USER_ID}'::uuid, 'phthien@vinamilk.com.vn', '{hashed}', 'admin', '{MEMBER_ID}'::uuid, true, false, now(), now()) "
        f"ON CONFLICT (id) DO NOTHING"
    )

    op.execute(
        f"INSERT INTO members (id, full_name, email, is_deleted, created_at, updated_at) "
        f"VALUES ('{AI_MEMBER_ID}'::uuid, 'VCC Bot', 'ai@vcc.local', false, now(), now()) "
        f"ON CONFLICT (id) DO NOTHING"
    )

    op.execute(
        f"INSERT INTO game_rooms (id, white_player_id, black_player_id, status, game_type, "
        f"time_control, increment, is_reviewed, is_deleted, result, created_at, updated_at) "
        f"VALUES ('{GAME_ROOM_ID}'::uuid, '{MEMBER_ID}'::uuid, '{AI_MEMBER_ID}'::uuid, "
        f"'finished', 'chess', 600, 0, false, false, 'white_win', now(), now()) "
        f"ON CONFLICT (id) DO NOTHING"
    )

    for i, notation in enumerate(MOVES, start=1):
        op.execute(
            f"INSERT INTO move_history (id, room_id, move_number, notation, is_deleted, created_at, updated_at) "
            f"VALUES (gen_random_uuid(), '{GAME_ROOM_ID}'::uuid, {i}, '{notation}', false, now(), now())"
        )


def downgrade() -> None:
    op.execute(f"DELETE FROM move_history WHERE room_id = '{GAME_ROOM_ID}'::uuid")
    op.execute(f"DELETE FROM game_rooms WHERE id = '{GAME_ROOM_ID}'::uuid")
    op.execute(f"DELETE FROM users WHERE id = '{USER_ID}'::uuid")
    op.execute(f"DELETE FROM members WHERE id = '{MEMBER_ID}'::uuid")

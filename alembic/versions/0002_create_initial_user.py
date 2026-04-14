"""create initial admin user

Revision ID: 0002_create_initial_user
Revises: 0001_initial
Create Date: 2026-04-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0002_create_initial_user'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert an initial admin user.

    NOTE: The password is hashed using the application's password hasher.
    """
    # Import application password hasher
    try:
        from app.core.security import get_password_hash
    except Exception:
        get_password_hash = None

    email = 'admin@example.com'
    plain_password = 'admin123'

    if get_password_hash:
        hashed = get_password_hash(plain_password)
    else:
        # Fallback: store plaintext (not recommended)
        hashed = plain_password

    created_at = datetime.utcnow()

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO users (email, hashed_password, is_active, is_superuser, created_at) VALUES (:email, :hp, :active, :super, :created)"
        ),
        {
            "email": email,
            "hp": hashed,
            "active": True,
            "super": True,
            "created": created_at,
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE email = :email"), {"email": 'admin@example.com'})

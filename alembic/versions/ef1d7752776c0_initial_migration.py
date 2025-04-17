"""initial migration

Revision ID: ef1d775276c0
Revises: 
Create Date: 2024-04-20 21:20:32.839580

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = 'ef1d775276c0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ### Fix: Add `extend_existing=True` to prevent duplicate table conflicts ###
    users_table = sa.Table(
        "users",
        sa.MetaData(),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('nickname', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.String(length=500), nullable=True),
        sa.Column('profile_picture_url', sa.String(length=255), nullable=True),
        sa.Column('linkedin_profile_url', sa.String(length=255), nullable=True),
        sa.Column('github_profile_url', sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum("ANONYMOUS", "AUTHENTICATED", "MANAGER", "ADMIN", name = 'Userrole'), nullable=False),
        sa.Column('is_professional', sa.Boolean(), nullable=True),
        sa.Column('professional_status_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        extend_existing=True,  # ✅ Prevents duplicate table errors
    )

    op.create_table(users_table)
    
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_nickname'), 'users', ['nickname'], unique=True)

def downgrade() -> None:
    # ### Keep the downgrade logic to remove indexes/tables if needed ###
    op.drop_index(op.f('ix_users_nickname'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
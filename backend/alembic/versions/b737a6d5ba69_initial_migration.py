"""initial migration

Revision ID: b737a6d5ba69
Revises: 
Create Date: 2024-12-05 15:32:33.764199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import String


# revision identifiers, used by Alembic.
revision: str = 'b737a6d5ba69'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('email', String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('password_hash', String(), nullable=False),
    sa.Column('mobili_url', String(), nullable=True),
    sa.Column('chat_id', sa.BigInteger(), nullable=True),
    sa.Column('is_task_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_chat_id'), 'user', ['chat_id'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_chat_id'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###

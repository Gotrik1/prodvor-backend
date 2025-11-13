"""Add FriendRequestStatus enum

Revision ID: 321b43a582f9
Revises: 2fd756909650
Create Date: 2025-11-12 23:27:38.436667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '321b43a582f9'
down_revision = '2fd756909650'
branch_labels = None
depends_on = None

def upgrade():
    friendrequeststatus = sa.Enum('pending', 'accepted', 'declined', name='friendrequeststatus')
    friendrequeststatus.create(op.get_bind(), checkfirst=True)
    op.alter_column('friend_requests', 'status',
               existing_type=sa.VARCHAR(),
               type_=friendrequeststatus,
               existing_nullable=False,
               postgresql_using='status::friendrequeststatus')
    op.drop_constraint('_user_team_uc', 'team_applications', type_='unique')


def downgrade():
    op.create_unique_constraint('_user_team_uc', 'team_applications', ['user_id', 'team_id'])
    op.alter_column('friend_requests', 'status',
               existing_type=sa.Enum('pending', 'accepted', 'declined', name='friendrequeststatus'),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    friendrequeststatus = sa.Enum('pending', 'accepted', 'declined', name='friendrequeststatus')
    friendrequeststatus.drop(op.get_bind())

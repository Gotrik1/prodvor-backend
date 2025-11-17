"""Rename captain_id to owner_id in teams table
Revision ID: a14319821c8b
Revises: 6d3fa08029f7
Create Date: 2025-11-16 13:52:37.236057
"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision = 'a14319821c8b'
down_revision = '6d3fa08029f7'
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('captain_id', new_column_name='owner_id')
        batch_op.drop_constraint('fk_teams_captain_id_users', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_teams_owner_id_users'), 'users', ['owner_id'], ['id'])
def downgrade():
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('owner_id', new_column_name='captain_id')
        batch_op.drop_constraint(batch_op.f('fk_teams_owner_id_users'), type_='foreignkey')
        batch_op.create_foreign_key('fk_teams_captain_id_users', 'users', ['captain_id'], ['id'])

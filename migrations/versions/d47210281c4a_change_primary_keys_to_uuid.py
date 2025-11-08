"""Change primary keys to UUID

Revision ID: d47210281c4a
Revises: bcc80b55f2f1
Create Date: 2025-11-08 19:23:34.139621

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd47210281c4a'
down_revision = 'bcc80b55f2f1'
branch_labels = None
depends_on = None


# Define all relationships that need to be dropped and re-created
# (table_with_fk, fk_name, target_table, fk_column)
foreign_keys = [
    ('comment', 'comment_postId_fkey', 'post', 'postId'),
    ('comment', 'comment_authorId_fkey', 'user', 'authorId'),
    ('coach_profile', 'coach_profile_userId_fkey', 'user', 'userId'),
    ('player_profile', 'player_profile_userId_fkey', 'user', 'userId'),
    ('post', 'post_authorId_fkey', 'user', 'authorId'),
    ('post', 'post_teamId_fkey', 'team', 'teamId'),
    ('referee_profile', 'referee_profile_userId_fkey', 'user', 'userId'),
    ('team', 'team_captainId_fkey', 'user', 'captainId'),
    # Assuming mvp and top scorer are also user ids
    ('team', 'team_mvpPlayerId_fkey', 'user', 'mvpPlayerId'),
    ('team', 'team_topScorerPlayerId_fkey', 'user', 'topScorerPlayerId'),
    ('team_applications', 'team_applications_userId_fkey', 'user', 'userId'),
    ('team_applications', 'team_applications_teamId_fkey', 'team', 'teamId'),
    ('team_followers', 'team_followers_userId_fkey', 'user', 'userId'),
    ('team_followers', 'team_followers_teamId_fkey', 'team', 'teamId'),
    ('team_members', 'team_members_userId_fkey', 'user', 'userId'),
    ('team_members', 'team_members_teamId_fkey', 'team', 'teamId'),
    ('team_season_stats', 'team_season_stats_teamId_fkey', 'team', 'teamId'),
    ('uploads', 'uploads_user_id_fkey', 'user', 'user_id'),
    ('user_sessions', 'user_sessions_userId_fkey', 'user', 'userId'),
    ('user_sports', 'user_sports_userId_fkey', 'user', 'userId'),
]

# Define all columns that need their type changed
# (table, column, old_type_for_using_clause, is_pk)
columns_to_migrate = [
    ('user', 'id', 'VARCHAR', True),
    ('team', 'id', 'INTEGER', True),
    ('achievement', 'id', 'INTEGER', True),
    ('coach_profile', 'id', 'INTEGER', True),
    ('comment', 'id', 'INTEGER', True),
    ('player_profile', 'id', 'INTEGER', True),
    ('playground', 'id', 'INTEGER', True),
    ('post', 'id', 'INTEGER', True),
    ('quest', 'id', 'INTEGER', True),
    ('referee_profile', 'id', 'INTEGER', True),
    ('sponsor', 'id', 'INTEGER', True),
    ('team_season_stats', 'id', 'INTEGER', True),
    ('tournament', 'id', 'INTEGER', True),
    ('user_sessions', 'id', 'INTEGER', True),
    ('uploads', 'id', 'VARCHAR', True),
    # Non-PK columns
    ('coach_profile', 'userId', 'VARCHAR', False),
    ('comment', 'postId', 'INTEGER', False),
    ('comment', 'authorId', 'VARCHAR', False),
    ('player_profile', 'userId', 'VARCHAR', False),
    ('post', 'authorId', 'VARCHAR', False),
    ('post', 'teamId', 'INTEGER', False),
    ('referee_profile', 'userId', 'VARCHAR', False),
    ('team', 'captainId', 'VARCHAR', False),
    ('team', 'mvpPlayerId', 'VARCHAR', False),
    ('team', 'topScorerPlayerId', 'VARCHAR', False),
    ('team_applications', 'userId', 'VARCHAR', False),
    ('team_applications', 'teamId', 'INTEGER', False),
    ('team_followers', 'userId', 'VARCHAR', False),
    ('team_followers', 'teamId', 'INTEGER', False),
    ('team_members', 'userId', 'VARCHAR', False),
    ('team_members', 'teamId', 'INTEGER', False),
    ('team_season_stats', 'teamId', 'INTEGER', False),
    ('uploads', 'user_id', 'VARCHAR', False),
    ('user_sessions', 'userId', 'VARCHAR', False),
    ('user_sports', 'userId', 'VARCHAR', False),
]

def upgrade():
    # Enable pgcrypto extension to generate UUIDs
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # STEP 1: Drop all foreign key constraints
    for table, fk_name, _, _ in foreign_keys:
        op.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{fk_name}";')

    # STEP 2: Alter all column types
    for table, column, old_type, is_pk in columns_to_migrate:
        # Determine the correct USING clause
        if old_type == 'INTEGER':
            using_clause = f"('00000000-0000-0000-0000-' || lpad(\"{column}\"::text, 12, '0'))::uuid"
        else:  # VARCHAR
            using_clause = f'"{column}"::uuid'

        if is_pk:
            pk_name = f"{table}_pkey"
            op.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{pk_name}";')
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" DROP DEFAULT;')
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE UUID USING {using_clause};')
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" SET DEFAULT gen_random_uuid();')
            op.execute(f'ALTER TABLE "{table}" ADD CONSTRAINT "{pk_name}" PRIMARY KEY ("{column}");')
        else:
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE UUID USING {using_clause};')

    # STEP 3: Re-create all foreign key constraints
    for table, fk_name, target_table, fk_column in foreign_keys:
        op.execute(f'ALTER TABLE "{table}" ADD CONSTRAINT "{fk_name}" FOREIGN KEY ("{fk_column}") REFERENCES "{target_table}" (id);')


def downgrade():
    # Downgrading is extremely complex and not recommended.
    pass

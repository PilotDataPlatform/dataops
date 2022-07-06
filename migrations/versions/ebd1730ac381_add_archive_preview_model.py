"""add_archive_preview_model

Revision ID: ebd1730ac381
Revises: 
Create Date: 2022-07-05 13:38:12.607701

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
#
# from models.api_archive_sql import BIGSERIAL


# revision identifiers, used by Alembic.
revision = 'ebd1730ac381'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'archive_preview',
        sa.Column('id', sa.BigInteger),
        sa.Column('file_id', postgresql.UUID(as_uuid=True)),
        sa.Column('archive_preview', sa.VARCHAR),
        sa.PrimaryKeyConstraint('id'),
        schema='public',
    )


def downgrade() -> None:
    op.drop_table('archive_preview', schema='public')
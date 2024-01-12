"""edit_db_39(arrival status)

Revision ID: 8dd7b5f5321c
Revises: 7bbb10f46805
Create Date: 2023-12-03 08:36:55.522442

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8dd7b5f5321c'
down_revision = '7bbb10f46805'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    enum = postgresql.ENUM('student', 'maintainer', 'team_leader', name='arrival_status_enum', create_type=False)
    enum.create(op.get_bind(), checkfirst=True)
    op.add_column('arrival', sa.Column('status', enum, nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('arrival', 'status')
    # ### end Alembic commands ###

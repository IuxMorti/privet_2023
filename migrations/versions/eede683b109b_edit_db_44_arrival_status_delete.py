"""edit_db_44(arrival status delete)

Revision ID: eede683b109b
Revises: 8699201b5898
Create Date: 2023-12-03 09:17:40.151042

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'eede683b109b'
down_revision = '8699201b5898'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('arrival', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('arrival', sa.Column('status', postgresql.ENUM('student', 'maintainer', 'team_leader', name='arrival_status_enum'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###

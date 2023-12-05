"""edit_db_41(arrival status delete)

Revision ID: b96dd1cd07c6
Revises: a1c2e36421a3
Create Date: 2023-12-03 09:12:04.853921

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b96dd1cd07c6'
down_revision = 'a1c2e36421a3'
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
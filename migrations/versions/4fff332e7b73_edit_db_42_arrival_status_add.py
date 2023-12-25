"""edit_db_42(arrival status add)

Revision ID: 4fff332e7b73
Revises: b96dd1cd07c6
Create Date: 2023-12-03 09:12:32.312098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4fff332e7b73'
down_revision = 'b96dd1cd07c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    enum = postgresql.ENUM('active', 'completed', 'awaiting_approval', name='arrival_status_enum', create_type=False)
    enum.create(op.get_bind(), checkfirst=True)
    op.add_column('arrival', sa.Column('status', enum, nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('arrival', 'status')
    # ### end Alembic commands ###

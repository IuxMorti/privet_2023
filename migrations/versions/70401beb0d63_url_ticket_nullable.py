"""url_ticket nullable

Revision ID: 70401beb0d63
Revises: 3b68429d8606
Create Date: 2024-01-13 18:48:03.035815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70401beb0d63'
down_revision = '3b68429d8606'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arrival', 'url_ticket',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arrival', 'url_ticket',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###

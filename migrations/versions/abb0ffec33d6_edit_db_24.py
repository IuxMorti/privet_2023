"""edit_db_24

Revision ID: abb0ffec33d6
Revises: a5678816d7ef
Create Date: 2023-12-01 11:31:28.389790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abb0ffec33d6'
down_revision = 'a5678816d7ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=False)
    # ### end Alembic commands ###
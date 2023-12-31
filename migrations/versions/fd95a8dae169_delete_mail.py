"""delete_mail

Revision ID: fd95a8dae169
Revises: a6ee3b6757d5
Create Date: 2023-11-09 12:50:24.012543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd95a8dae169'
down_revision = 'a6ee3b6757d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'mail')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('mail', sa.VARCHAR(length=318), autoincrement=False, nullable=False))
    # ### end Alembic commands ###

"""edit_db_27

Revision ID: 019261712a80
Revises: 45707bab3bc4
Create Date: 2023-12-01 12:12:06.863448

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '019261712a80'
down_revision = '45707bab3bc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    enum = postgresql.ENUM('WAITING_FOR_WORKER', 'IN_PROGRESS', 'DONE',name='order_status_enum', create_type=False)
    enum.create(op.get_bind(), checkfirst=True)
    op.add_column('role', sa.Column('status', enum, nullable=False))
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=True)
    op.drop_column('role', 'status')
    # ### end Alembic commands ###

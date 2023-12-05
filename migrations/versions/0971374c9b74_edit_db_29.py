"""edit_db_29

Revision ID: 0971374c9b74
Revises: b0dd76c99c5b
Create Date: 2023-12-01 12:34:08.923810

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0971374c9b74'
down_revision = 'b0dd76c99c5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=False)
    op.drop_column('role', 'status')
    op.drop_constraint('user_role_id_fkey', 'user', type_='foreignkey')
    op.drop_column('user', 'role_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role_id', sa.UUID(), autoincrement=False, nullable=False))
    op.create_foreign_key('user_role_id_fkey', 'user', 'role', ['role_id'], ['id'])
    op.add_column('role', sa.Column('status', postgresql.ENUM('WAITING_FOR_WORKER', 'IN_PROGRESS', 'DONE', name='order_status_enum'), autoincrement=False, nullable=False))
    op.alter_column('role', 'title',
               existing_type=sa.VARCHAR(length=130),
               nullable=True)
    # ### end Alembic commands ###
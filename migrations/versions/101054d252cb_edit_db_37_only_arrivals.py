"""edit_db_37(only arrivals)

Revision ID: 101054d252cb
Revises: e8ea521844db
Create Date: 2023-12-02 08:56:11.205412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '101054d252cb'
down_revision = 'e8ea521844db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_arrival',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('arrival_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'arrival_id', name='idx_unique_user_arrival')
    )
    op.drop_table('buddy_arrival')
    op.drop_constraint('user_student_arrival_id_fkey', 'user', type_='foreignkey')
    op.drop_column('user', 'student_arrival_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('student_arrival_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('user_student_arrival_id_fkey', 'user', 'arrival', ['student_arrival_id'], ['id'])
    op.create_table('buddy_arrival',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('buddy_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('arrival_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], name='buddy_arrival_arrival_id_fkey'),
    sa.ForeignKeyConstraint(['buddy_id'], ['user.id'], name='buddy_arrival_buddy_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='buddy_arrival_pkey'),
    sa.UniqueConstraint('buddy_id', 'arrival_id', name='idx_unique_buddy_arrival')
    )
    op.drop_table('user_arrival')
    # ### end Alembic commands ###

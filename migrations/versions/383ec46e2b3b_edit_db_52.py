"""edit_db_52

Revision ID: 383ec46e2b3b
Revises: 55087e5bda43
Create Date: 2023-12-07 13:32:17.248120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '383ec46e2b3b'
down_revision = '55087e5bda43'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('buddy_arrival',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('buddy_id', sa.UUID(), nullable=False),
    sa.Column('arrival_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], ),
    sa.ForeignKeyConstraint(['buddy_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('buddy_id', 'arrival_id', name='idx_unique_buddy_arrival')
    )
    op.create_table('student_arrival',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('student_id', sa.UUID(), nullable=False),
    sa.Column('arrival_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'arrival_id', name='idx_unique_student_arrival')
    )
    op.drop_table('user_arrival')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('gender', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('buddy_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('visa_end_date', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('living_place', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('study_direction', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('payment_status', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('institute', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('user', 'is_confirmed_buddy')
    op.drop_column('user', 'accommodation')
    op.drop_column('user', 'last_visa_expiration')
    op.drop_column('user', 'study_program')
    op.drop_column('user', 'is_escort_paid')
    op.drop_column('user', 'university')
    op.drop_column('user', 'sex')
    op.create_table('user_arrival',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('arrival_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['arrival_id'], ['arrival.id'], name='user_arrival_arrival_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_arrival_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_arrival_pkey'),
    sa.UniqueConstraint('user_id', 'arrival_id', name='idx_unique_user_arrival')
    )
    op.drop_table('student_arrival')
    op.drop_table('buddy_arrival')
    # ### end Alembic commands ###
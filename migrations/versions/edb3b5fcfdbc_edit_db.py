"""edit_db

Revision ID: edb3b5fcfdbc
Revises: 442e3096372e
Create Date: 2023-11-19 14:18:50.674527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edb3b5fcfdbc'
down_revision = '442e3096372e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('language',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('language', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_language',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('language_id', sa.UUID(), nullable=False),
    sa.Column('level', sa.String(length=2), nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'language_id', 'level', name='idx_unique_user_language')
    )
    op.drop_table('language_level')
    op.drop_table('user_language_level')
    op.add_column('user', sa.Column('phone', sa.String(length=12), nullable=True))
    op.add_column('user', sa.Column('telegram', sa.String(length=32), nullable=True))
    op.add_column('user', sa.Column('whatsapp', sa.String(length=12), nullable=True))
    op.add_column('user', sa.Column('vk', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'vk')
    op.drop_column('user', 'whatsapp')
    op.drop_column('user', 'telegram')
    op.drop_column('user', 'phone')
    op.create_table('user_language_level',
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('language_level_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['language_level_id'], ['language_level.id'], name='user_language_level_language_level_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_language_level_user_id_fkey')
    )
    op.create_table('language_level',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('language', sa.VARCHAR(length=30), autoincrement=False, nullable=False),
    sa.Column('level', sa.VARCHAR(length=2), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='language_level_pkey'),
    sa.UniqueConstraint('language', 'level', name='language_level_language_level_key')
    )
    op.drop_table('user_language')
    op.drop_table('language')
    # ### end Alembic commands ###

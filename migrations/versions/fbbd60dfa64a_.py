"""empty message

Revision ID: fbbd60dfa64a
Revises: f1dd3fed376f
Create Date: 2019-07-29 22:33:49.106590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbbd60dfa64a'
down_revision = 'f1dd3fed376f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('filter_unspsc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('unspsc_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['unspsc_id'], ['unspsc.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('user_unspsc_filter')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_unspsc_filter',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('unspsc_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['unspsc_id'], ['unspsc.id'], name='user_unspsc_filter_unspsc_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_unspsc_filter_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'unspsc_id', name='user_unspsc_filter_pkey')
    )
    op.drop_table('filter_unspsc')
    # ### end Alembic commands ###

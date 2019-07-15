"""empty message

Revision ID: ae3b544ed6db
Revises: bed95f45c0e8
Create Date: 2019-07-11 20:57:31.167209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae3b544ed6db'
down_revision = 'bed95f45c0e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('op', 'close_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('op', sa.Column('close_date', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###

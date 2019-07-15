"""empty message

Revision ID: 1cff2176fa82
Revises: ec0d929af0cc
Create Date: 2019-07-11 22:12:59.413887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cff2176fa82'
down_revision = 'ec0d929af0cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('op', sa.Column('publish_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('op', 'publish_date')
    # ### end Alembic commands ###
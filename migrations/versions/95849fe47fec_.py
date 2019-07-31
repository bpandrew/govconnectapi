"""empty message

Revision ID: 95849fe47fec
Revises: aab57d9b330e
Create Date: 2019-07-30 21:21:08.412354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95849fe47fec'
down_revision = 'aab57d9b330e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract', sa.Column('atm_austender_id', sa.String(), nullable=True))
    op.add_column('contract', sa.Column('panel_austender_id', sa.String(), nullable=True))
    op.add_column('contract', sa.Column('son_austender_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contract', 'son_austender_id')
    op.drop_column('contract', 'panel_austender_id')
    op.drop_column('contract', 'atm_austender_id')
    # ### end Alembic commands ###
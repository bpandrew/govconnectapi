"""empty message

Revision ID: bd6717a96d7e
Revises: e0552fec24f3
Create Date: 2019-08-10 08:10:37.603658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd6717a96d7e'
down_revision = 'e0552fec24f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract_count', sa.Column('aps_notification_no', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contract_count', 'aps_notification_no')
    # ### end Alembic commands ###

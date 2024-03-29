"""empty message

Revision ID: 309b52aa8a36
Revises: bd6717a96d7e
Create Date: 2019-08-10 08:12:57.054138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '309b52aa8a36'
down_revision = 'bd6717a96d7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract_count', sa.Column('aps_notification', sa.Integer(), nullable=True))
    op.drop_column('contract_count', 'aps_notification_no')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract_count', sa.Column('aps_notification_no', sa.DATE(), autoincrement=False, nullable=True))
    op.drop_column('contract_count', 'aps_notification')
    # ### end Alembic commands ###

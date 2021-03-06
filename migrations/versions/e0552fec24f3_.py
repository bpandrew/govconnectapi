"""empty message

Revision ID: e0552fec24f3
Revises: d40be90e16fc
Create Date: 2019-08-08 08:23:34.005927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0552fec24f3'
down_revision = 'd40be90e16fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplier', sa.Column('display_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('supplier', 'display_name')
    # ### end Alembic commands ###

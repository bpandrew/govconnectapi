"""empty message

Revision ID: 372774ba2961
Revises: 975e4c9c80ce
Create Date: 2019-08-13 10:00:15.276378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '372774ba2961'
down_revision = '975e4c9c80ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplier', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'supplier', 'supplier_address', ['address_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'supplier', type_='foreignkey')
    op.drop_column('supplier', 'address_id')
    # ### end Alembic commands ###
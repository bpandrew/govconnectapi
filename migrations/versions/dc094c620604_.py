"""empty message

Revision ID: dc094c620604
Revises: 524bce2938b5
Create Date: 2019-08-18 09:13:10.891569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc094c620604'
down_revision = '524bce2938b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('competitor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.Date(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('supplier_id', sa.Integer(), nullable=True),
    sa.Column('competitor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['competitor_id'], ['supplier.id'], ),
    sa.ForeignKeyConstraint(['supplier_id'], ['supplier.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('competitor')
    # ### end Alembic commands ###

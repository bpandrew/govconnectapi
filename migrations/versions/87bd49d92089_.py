"""empty message

Revision ID: 87bd49d92089
Revises: 387f0a110926
Create Date: 2019-07-08 16:41:24.854554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87bd49d92089'
down_revision = '387f0a110926'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('opportunities', sa.Column('atm_id', sa.String(), nullable=True))
    op.drop_column('opportunities', 'opportunity_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('opportunities', sa.Column('opportunity_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('opportunities', 'atm_id')
    # ### end Alembic commands ###
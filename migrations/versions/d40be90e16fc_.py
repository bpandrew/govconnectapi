"""empty message

Revision ID: d40be90e16fc
Revises: a4fe457041e0
Create Date: 2019-08-08 08:15:19.200425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd40be90e16fc'
down_revision = 'a4fe457041e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('level', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('agency', sa.Column('blurb', sa.String(), nullable=True))
    op.add_column('agency', sa.Column('display_title', sa.String(), nullable=True))
    op.add_column('branch', sa.Column('display_title', sa.String(), nullable=True))
    op.add_column('contract', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contract', 'role', ['role_id'], ['id'])
    op.add_column('division', sa.Column('display_title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('division', 'display_title')
    op.drop_constraint(None, 'contract', type_='foreignkey')
    op.drop_column('contract', 'role_id')
    op.drop_column('branch', 'display_title')
    op.drop_column('agency', 'display_title')
    op.drop_column('agency', 'blurb')
    op.drop_table('role')
    # ### end Alembic commands ###
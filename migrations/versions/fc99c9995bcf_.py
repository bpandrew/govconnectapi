"""empty message

Revision ID: fc99c9995bcf
Revises: d0093fbd38b8
Create Date: 2019-08-01 14:53:09.439517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc99c9995bcf'
down_revision = 'd0093fbd38b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('agency_division')
    op.drop_table('division_branch')
    op.add_column('branch', sa.Column('division_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'branch', 'division', ['division_id'], ['id'])
    op.add_column('division', sa.Column('agency_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'division', 'agency', ['agency_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'division', type_='foreignkey')
    op.drop_column('division', 'agency_id')
    op.drop_constraint(None, 'branch', type_='foreignkey')
    op.drop_column('branch', 'division_id')
    op.create_table('division_branch',
    sa.Column('division_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('branch_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['branch_id'], ['branch.id'], name='division_branch_branch_id_fkey'),
    sa.ForeignKeyConstraint(['division_id'], ['division.id'], name='division_branch_division_id_fkey'),
    sa.PrimaryKeyConstraint('division_id', 'branch_id', name='division_branch_pkey')
    )
    op.create_table('agency_division',
    sa.Column('agency_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('division_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['agency_id'], ['agency.id'], name='agency_division_agency_id_fkey'),
    sa.ForeignKeyConstraint(['division_id'], ['division.id'], name='agency_division_division_id_fkey'),
    sa.PrimaryKeyConstraint('agency_id', 'division_id', name='agency_division_pkey')
    )
    # ### end Alembic commands ###
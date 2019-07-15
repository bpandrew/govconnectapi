"""empty message

Revision ID: b919fffa40e8
Revises: d7478414e98c
Create Date: 2019-07-10 14:41:27.786767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b919fffa40e8'
down_revision = 'd7478414e98c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('books')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('author', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('published', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'books_pkey')
    )
    # ### end Alembic commands ###
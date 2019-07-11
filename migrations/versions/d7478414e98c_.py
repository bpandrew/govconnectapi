"""empty message

Revision ID: d7478414e98c
Revises: c34b7e5648e3
Create Date: 2019-07-10 14:34:39.280702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7478414e98c'
down_revision = 'c34b7e5648e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_identifier')
    op.drop_table('students')
    op.drop_table('classes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('classes',
    sa.Column('class_id', sa.INTEGER(), server_default=sa.text(u"nextval('classes_class_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('class_name', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('class_id', name=u'classes_pkey'),
    sa.UniqueConstraint('class_name', name=u'classes_class_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('students',
    sa.Column('user_id', sa.INTEGER(), server_default=sa.text(u"nextval('students_user_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('user_fistName', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('user_lastName', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('user_email', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('user_id', name=u'students_pkey'),
    sa.UniqueConstraint('user_email', name=u'students_user_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('student_identifier',
    sa.Column('class_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['class_id'], [u'classes.class_id'], name=u'student_identifier_class_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'students.user_id'], name=u'student_identifier_user_id_fkey')
    )
    # ### end Alembic commands ###

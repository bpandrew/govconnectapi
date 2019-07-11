from app import db
from app import ma


unspsc_op = db.Table('unspsc_op',
    db.Column('unspsc_id', db.Integer, db.ForeignKey('unspsc.id'), primary_key=True),
    db.Column('op_id', db.Integer, db.ForeignKey('op.id'), primary_key=True)
)


class Op(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True)
    atm_id = db.Column(db.String(), index=True)

class OpSchema(ma.ModelSchema):
    class Meta:
       model = Op
    categories = ma.Nested("UnspscSchema", many=True, only=("id", "unspsc"))



class Unspsc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unspsc = db.Column(db.String())
    title = db.Column(db.String())
    level  = db.Column(db.String())
    parent_id = db.Column(db.Integer())
    opportunities = db.relationship('Op', secondary=unspsc_op, lazy='subquery', backref=db.backref('categories', lazy=True))

class UnspscSchema(ma.ModelSchema):
    class Meta:
       model = Unspsc
    #opportunities = ma.Nested("OpSchema", many=True, only=("id", "title"))


class UnspscSchemaSimple(ma.ModelSchema):
    class Meta:
       model = Unspsc
    #opportunities = ma.Nested("OpSchema", many=True, only=("id", "title"))



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True)

class UserSchema(ma.ModelSchema):
    class Meta:
       model = User
       #fields = ('id', 'full_name')

    comments = ma.Nested("CommentSchema", many=True, exclude=("email",))




class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="comments")

class CommentSchema(ma.ModelSchema):
    class Meta:
       model = Comment

    user = ma.Nested(UserSchema, only=("id", "full_name"))



tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('page_id', db.Integer, db.ForeignKey('page.id'), primary_key=True)
)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('pages', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
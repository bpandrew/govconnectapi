from app import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    author = db.Column(db.String())
    published = db.Column(db.String())

    def __init__(self, name, author, published):
        self.name = name
        self.author = author
        self.published = published

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'author': self.author,
            'published':self.published
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String())

    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email':self.email
        }


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    atm_id = db.Column(db.String())
    categories = db.relationship("Unspsc", secondary="orders")

    #categories = db.relationship('Unspsc', secondary=unspscs, lazy='select', backref=db.backref('opportunities', lazy=True))
    #unspscs = db.relationship('Unspsc', secondary=unspscs, lazy=False)

    #unspscid_segment = db.relationship("Unspsc", primaryjoin = "Opportunity.unspscid_segment_id == Unspsc.id", backref="categories")
    #unspscid_segment = db.relationship("Unspsc", backref="opportunities", lazy=True)
    #unspscid_segment = db.relationship("Unspsc", foreign_keys=[unspscid_segment_id])
        
    
    #unspscid_segment = db.Column(db.Integer(), nullable=True)
    #unspscid_family = db.Column(db.Integer(), nullable=True)
    #unspscid_class = db.Column(db.Integer(), nullable=True)
    #unspscid_commodity = db.Column(db.Integer(), nullable=True)

    def __init__(self, title, atm_id, categories):
        self.title = title
        self.atm_id = atm_id
        self.categories = categories
        #self.unspscid_segment_id = unspscid_segment_id
        #self.unspscid_family = unspscid_family
        #self.unspscid_class = unspscid_class
        #self.unspscid_commodity = unspscid_commodity

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'title': self.title,
            'atm_id': self.atm_id,
            'categories': self.categories
            #'unspscid_segment_id': self.unspscid_segment_id
            #'unspscid_family': self.unspscid_family,
            #'unspscid_class': self.unspscid_class,
            #'unspscid_commodity': self.unspscid_commodity
        }


class Unspsc(db.Model):
    __tablename__ = 'unspsc'

    id = db.Column(db.Integer, primary_key=True)
    unspsc = db.Column(db.Integer())
    title = db.Column(db.String(), nullable=True)
    level = db.Column(db.String())
    parent_id = db.Column(db.Integer(), nullable=True)

    opportunities = db.relationship("Opportunity", secondary="orders")
    #opportunity = db.relationship('Opportunity', backref='unspsc', lazy='joined')
    
    def __init__(self, unspsc, title, level, parent_id):
        self.unspsc = unspsc
        self.title = title
        self.level = level
        self.parent_id = parent_id


    def __repr__(self):
        return '<id {}>'.format(self.id)
    

    def serialize(self):
        return {
            'id': self.id, 
            'unspsc': self.unspsc,
            'title': self.title,
            'level': self.level,
            'parent_id': self.parent_id
        }


class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    opp_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
    un_id = db.Column(db.Integer, db.ForeignKey('unspsc.id'))

    opp = db.relationship(Opportunity, backref=db.backref("orders", cascade="all, delete-orphan"))
    un = db.relationship(Unspsc, backref=db.backref("orders", cascade="all, delete-orphan"))


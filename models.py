from app import db
from app import ma



# -------------- AGENCY ---------------

class Agency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    portfolio = db.Column(db.String(), nullable=True)


class AgencySchema(ma.ModelSchema):
    class Meta:
       model = Agency
    opportunities = ma.Nested("OpSchema") #, only=("id", "title")
    contracts = ma.Nested("ContractSchema") #, only=("id", "title")



# --------------- LOCATION -----------------

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

class LocationSchema(ma.ModelSchema):
    class Meta:
       model = Location
    #opportunities = ma.Nested("OpSchema") #, only=("id", "title")


# --------------- ADDENDUM -----------------

class Addenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    published = db.Column(db.Date())


class AddendaSchema(ma.ModelSchema):
    class Meta:
       model = Addenda



# --------------- OPPORTUNITIES ------------------

unspsc_op = db.Table('unspsc_op',
    db.Column('unspsc_id', db.Integer, db.ForeignKey('unspsc.id'), primary_key=True),
    db.Column('op_id', db.Integer, db.ForeignKey('op.id'), primary_key=True)
)

class Op(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    atm_id = db.Column(db.String())
    conditions_for_participation = db.Column(db.String(), nullable=True)
    panel_arrangement = db.Column(db.Integer(), nullable=True)
    timeframe_for_delivery = db.Column(db.String(), nullable=True)
    close_date = db.Column(db.Date(), nullable=True)  #close_date_&_time
    multi_stage = db.Column(db.Integer(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    address_for_lodgement = db.Column(db.String(), nullable=True)
    publish_date = db.Column(db.Date())
    atm_type = db.Column(db.String(), nullable=True)
    multi_agency_access = db.Column(db.Integer(), nullable=True)
    document_link = db.Column(db.String(), nullable=True)
    #addenda_available = db.Column(db.String())
    #estimated_value = db.Column(db.String()) #estimated_value_(aud)
    #location = db.Column(db.String()) ## NEEDS WORK act, nsw, vic, sa, wa, qld, nt, tas"

    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"))
    agency = db.relationship("Agency", backref="opportunities")

   


class OpSchema(ma.ModelSchema):
    class Meta:
       model = Op
       #fields = ("title",)
    categories = ma.Nested("UnspscSchema", many=True, only=("id", "unspsc", "title", "level_int"))
    agency = ma.Nested(AgencySchema, only=("id", "title"))


class OpSimpleSchema(ma.ModelSchema):
    categories = ma.Nested("UnspscSchema", many=True, only=("id", "unspsc", "title", "level_int"))
    agency = ma.Nested(AgencySchema, only=("id", "title"))
    class Meta:
       model = Op
       fields = ("id", "title", "publish_date", "close_date", "categories", "agency", "atm_type")





class Unspsc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unspsc = db.Column(db.String())
    title = db.Column(db.String())
    level  = db.Column(db.String())
    level_int = db.Column(db.Integer())
    parent_id = db.Column(db.Integer())
    scraped = db.Column(db.Integer(), default=0)
    opportunities = db.relationship('Op', secondary=unspsc_op, lazy='subquery', backref=db.backref('categories', lazy=True))

class UnspscSchema(ma.ModelSchema):
    class Meta:
       model = Unspsc
    #opportunities = ma.Nested("OpSchema", many=True, only=("id", "title"))


class UnspscSchemaSimple(ma.ModelSchema):
    class Meta:
       model = Unspsc
    #opportunities = ma.Nested("OpSchema", many=True, only=("id", "title"))



#----------  SUPPLIERS ----------

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abn = db.Column(db.String())
    name = db.Column(db.String())
    country = db.Column(db.String())

class SupplierSchema(ma.ModelSchema):
    class Meta:
       model = Supplier



#----------  SON ----------

class Son(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    austender_id = db.Column(db.String())
    austender_link = db.Column(db.String())

class SonSchema(ma.ModelSchema):
    class Meta:
       model = Supplier



#----------  CONTRACTS ----------

#{"cn_id:": "cn3609370", "postcode:": "2000", "title": "Legal Services", "name:": "norton rose", "contract_period:": "10-may-2019 to 30-jun-2019", "category:": "legal services", "atm_id:": "", "town/city:": "sydney", "postal_address:": "", "confidentiality_-_contract:": "no", "agency_reference_id:": "75489", "confidentiality_-_outputs:": "no", "contract_value_(aud):": "$84,700.00", "consultancy:": "no", "country:": "australia", "abn:": "32 720 868 049", "agency:": "australian competition and consumer commission", "procurement_method:": "prequalified tender", "description:": "legal services", "state/territory:": "nsw", "publish_date:": "11-jul-2019"}

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=True)
    cn_id = db.Column(db.String(), nullable=True)
    contract_start = db.Column(db.Date())
    contract_end = db.Column(db.Date())
    contract_duration = db.Column(db.Integer(), nullable=True)
    #category_id = db.Column(db.String(), nullable=True)
    #atm_id = db.Column(db.String(), nullable=True)
    confidentiality_contract = db.Column(db.String(), nullable=True)
    agency_reference_id = db.Column(db.String(), nullable=True)
    confidentiality_outputs = db.Column(db.String(), nullable=True)
    contract_value = db.Column(db.String(), nullable=True)
    procurement_method = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    publish_date = db.Column(db.Date())
    category_temp_title = db.Column(db.String(), nullable=True)
    atm_austender_id = db.Column(db.String(), nullable=True)

    son_id = db.Column(db.Integer, db.ForeignKey("son.id"), nullable=True)
    son = db.relationship("Son", backref="contracts")

    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)
    agency = db.relationship("Agency", backref="contracts")

    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
    supplier = db.relationship("Supplier", backref="contracts")

    unspsc_id = db.Column(db.Integer, db.ForeignKey("unspsc.id"), nullable=True)
    unspsc = db.relationship("Unspsc", backref="contracts")



class ContractSchema(ma.ModelSchema):
    class Meta:
       model = Contract
    agency = ma.Nested(AgencySchema, only=("id", "title"))
    supplier = ma.Nested(SupplierSchema, only=("id", "name", "abn", "country"))
    unspsc = ma.Nested(SupplierSchema, only=("id", "title", "unspsc", "level", "level_int", "parent_id"))
    son = ma.Nested(SonSchema, only=("id", "austender_id"))




#{'employee_first_name': u'Karen-Maree', 'agency_notice': u'Department of health', 'notice_no': u'10741900', u'classification': u'APS Level 6', u'advertised': u'10736497: PS42-Thu, Thursday, 18 October 2018', u'agency_employment_act': u'PS Act 1999', u'agency': u'Department of Health', 'employee_no': u'608-76477', 'notice_type': u'Promotion', 'employee_last_name': u'Garside', 'classification_from': u'APS Level 5', u'location': u'Parramatta - NSW', u'position_details': u'Senior Investigator,  Investigation Section', u'position': u'18-PBID-2028', 'portfolio': u'health'}

#----------  APSJOBS ----------

class ApsEmployee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    employee_no = db.Column(db.String())

class ApsEmployeeSchema(ma.ModelSchema):
    class Meta:
       model = ApsEmployee



class ApsNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publish_date = db.Column(db.Date())
    notice_type = db.Column(db.String())

    aps_id = db.Column(db.Integer, db.ForeignKey("son.id"), nullable=True)
    aps = db.relationship("ApsEmployee", backref="notices")

    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)
    agency = db.relationship("Agency", backref="contracts")

    classification_from = db.Column(db.String())
    classification = db.Column(db.String())
    position_details = db.Column(db.String())
    position = db.Column(db.String())



class ApsNoticeSchema(ma.ModelSchema):
    class Meta:
       model = ApsNotice
    aps = ma.Nested(ApsEmployee, only=("id", "first_name", "last_name", "employee_no"))
    agency = ma.Nested(AgencySchema, only=("id", "title"))



#----------  USERS ----------


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    password = db.Column(db.String())
    token = db.Column(db.String())

class UserSchema(ma.ModelSchema):
    class Meta:
       model = User
       fields = ('id', 'first_name', 'last_name', 'email', 'token')
    comments = ma.Nested("CommentSchema", many=True, exclude=("email",))






class FilterUnspsc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", backref="filters")
    unspsc_id = db.Column(db.Integer, db.ForeignKey("unspsc.id"), nullable=True)
    unspsc = db.relationship("Unspsc", backref="filters")
    


class FilterUnspscSchema(ma.ModelSchema):
    class Meta:
       model = FilterUnspsc
    user = ma.Nested(UnspscSchema, only=("id", "first_name", "last_name"))
    unspsc = ma.Nested(UnspscSchema, only=("id", "title"))








class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="comments")

class CommentSchema(ma.ModelSchema):
    class Meta:
       model = Comment

    user = ma.Nested(UserSchema, only=("id", "full_name"))



#----------  MANY TO MANY ----------

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('page_id', db.Integer, db.ForeignKey('page.id'), primary_key=True)
)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('pages', lazy=True, cascade="all"))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
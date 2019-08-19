from app import db
from app import ma



# -------------- AGENCY ---------------


class Agency(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	display_title = db.Column(db.String)
	portfolio = db.Column(db.String(), nullable=True)
	image_url = db.Column(db.String(), nullable=True)
	blurb = db.Column(db.String)


class AgencySchema(ma.ModelSchema):
	class Meta:
		model = Agency
	#opportunities = ma.Nested("OpSchema") #, only=("id", "title")
	#contracts = ma.Nested("ContractSchema") #, only=("id", "title")
	divisions = ma.Nested("DivisionSchema", many=True, only=("id", "title", "branches", "display_title"))

class AgencySchemaSimple(ma.ModelSchema):
	class Meta:
		model = Agency
		fields = ("id", "display_title")


class Division(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String())
	display_title = db.Column(db.String)
	agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"))
	agency = db.relationship("Agency", backref="divisions")


class DivisionSchema(ma.ModelSchema):
	class Meta:
		model = Division
	branches = ma.Nested("BranchSchema", many=True, only=("id", "title", "display_title"))
    


class Branch(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String())
	display_title = db.Column(db.String)
	division_id = db.Column(db.Integer, db.ForeignKey("division.id"))
	division = db.relationship("Division", backref="branches")


class BranchSchema(ma.ModelSchema):
    class Meta:
       model = Branch


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
	agency = ma.Nested(AgencySchema, only=("id", "title", "display_title"))


class OpSimpleSchema(ma.ModelSchema):
	categories = ma.Nested("UnspscSchema", many=True, only=("id", "unspsc", "title", "level_int"))
	agency = ma.Nested(AgencySchema, only=("id", "title", "display_title"))
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
		fields = ("id", "unspsc", "title")






#----------  SUPPLIERS ----------

class Supplier(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	abn = db.Column(db.String())
	name = db.Column(db.String())
	display_name = db.Column(db.String())
	country = db.Column(db.String())
	image_url = db.Column(db.String(), nullable=True)
	umbrella = db.Column(db.Integer, nullable=True) #Is this an artificially created supplier to aggragate all of the ABNs
	umbrella_id = db.Column(db.Integer, nullable=True) #If this supplier sits under an umbrella co. what is the ID
	
class SupplierSchema(ma.ModelSchema):
	class Meta:	
		model = Supplier
		#fields = ("id", "name", "abn", "image_url", "display_name", "umbrella", "umbrella_id")
	addresses = ma.Nested("SupplierAddressSchema", many=True, only=("postal_address", "town_city", "postcode", "country", "correct_at"))


class SupplierMatrix(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	json = db.Column(db.JSON)
	matrix_type = db.Column(db.String)
	financial_year = db.Column(db.Integer)
	financial_quarter = db.Column(db.Integer)
	created = db.Column(db.Date())
	supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	supplier = db.relationship("Supplier", backref="matrixes")

class SupplierMatrixSchema(ma.ModelSchema):
	class Meta:
		model = SupplierMatrix
	supplier = ma.Nested(SupplierSchema, only=("id", "name", "abn", "country", "display_name", "umbrella", "umbrella_id"))


class Competitor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	created = db.Column(db.Date())
	score = db.Column(db.Float)
	supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	supplier = db.relationship("Supplier", foreign_keys=[supplier_id], backref="target_supplier")
	competitor_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	competitor = db.relationship("Supplier", foreign_keys=[competitor_id], backref="competitor")

class CompetitorSchema(ma.ModelSchema):
	class Meta:
		model = Competitor
	supplier = ma.Nested(SupplierSchema, only=("id", "name", "abn", "country", "display_name"))
	competitor = ma.Nested(SupplierSchema, only=("id", "name", "abn", "country", "display_name", "umbrella", "umbrella_id"))



#----------  SUPPLIER REGISTERED ADDRESS ----------

class SupplierAddress(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	postal_address = db.Column(db.String())
	town_city = db.Column(db.String)
	postcode = db.Column(db.String)  
	country = db.Column(db.String)
	correct_at = db.Column(db.Date())
	supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	supplier = db.relationship("Supplier", backref="addresses")
	

class SupplierAddressSchema(ma.ModelSchema):
    class Meta:
       model = SupplierAddress




#----------  INDIVIDUAL ROLE ----------

class Role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String())
	level = db.Column(db.String())

class RoleSchema(ma.ModelSchema):
	class Meta:
		model = Role


#----------  SON ----------

class Son(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    austender_id = db.Column(db.String())
    austender_link = db.Column(db.String())

class SonSchema(ma.ModelSchema):
    class Meta:
       model = Supplier


#----------  SCRAPER TRACKING ----------

class ContractCount(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	scrape_date = db.Column(db.Date())
	aps_notification = db.Column(db.Integer)


class ContractCountSchema(ma.ModelSchema):
	class Meta:
		model = ContractCount


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
	original_contract_value = db.Column(db.String(), nullable=True)
	procurement_method = db.Column(db.String(), nullable=True)
	description = db.Column(db.String(), nullable=True)
	publish_date = db.Column(db.Date())
	category_temp_title = db.Column(db.String(), nullable=True)
	atm_austender_id = db.Column(db.String(), nullable=True)
	contact_name = db.Column(db.String(), nullable=True)

	son_id = db.Column(db.Integer, db.ForeignKey("son.id"), nullable=True)
	son = db.relationship("Son", backref="contracts")

	agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)
	agency = db.relationship("Agency", backref="contracts")

	supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	supplier = db.relationship("Supplier", backref="contracts")

	unspsc_id = db.Column(db.Integer, db.ForeignKey("unspsc.id"), nullable=True)
	unspsc = db.relationship("Unspsc", backref="contracts")

	division_id = db.Column(db.Integer, db.ForeignKey("division.id"), nullable=True)
	division = db.relationship("Division", backref="contracts")

	branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=True)
	branch = db.relationship("Branch", backref="contracts")

	role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=True)
	role = db.relationship("Role", backref="contracts")



class ContractSchema(ma.ModelSchema):
	class Meta:
		model = Contract
	agency = ma.Nested(AgencySchema, only=("id", "title", "display_title"))
	supplier = ma.Nested(SupplierSchema, only=("id", "name", "abn", "country", "display_name", "umbrella", "umbrella_id"))
	unspsc = ma.Nested(UnspscSchema, only=("id", "title", "unspsc", "level", "level_int", "parent_id"))
	son = ma.Nested(SonSchema, only=("id", "austender_id"))
	division = ma.Nested(DivisionSchema, only=("id", "title", "display_title"))
	branch = ma.Nested(BranchSchema, only=("id", "title", "display_title"))
	role = ma.Nested(RoleSchema, only=("id", "title", "level"))



#{'employee_first_name': u'Karen-Maree', 'agency_notice': u'Department of health', 'notice_no': u'10741900', u'classification': u'APS Level 6', u'advertised': u'10736497: PS42-Thu, Thursday, 18 October 2018', u'agency_employment_act': u'PS Act 1999', u'agency': u'Department of Health', 'employee_no': u'608-76477', 'notice_type': u'Promotion', 'employee_last_name': u'Garside', 'classification_from': u'APS Level 5', u'location': u'Parramatta - NSW', u'position_details': u'Senior Investigator,  Investigation Section', u'position': u'18-PBID-2028', 'portfolio': u'health'}

#----------  APSJOBS ----------

class Employee(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String())
	last_name = db.Column(db.String())
	employee_no = db.Column(db.String())
	gender = db.Column(db.String()) 
	linkedin = db.Column(db.String, nullable=True)

class EmployeeSchema(ma.ModelSchema):
    class Meta:
       model = Employee
    notices = ma.Nested("NoticeSchema", many=True, exclude=("advertised",))



class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)
    employee = db.relationship("Employee", backref="notices")
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)
    agency = db.relationship("Agency", backref="notices")
    classification_from = db.Column(db.String(), nullable=True)
    classification = db.Column(db.String(), nullable=True)
    position_details = db.Column(db.String(), nullable=True)
    position = db.Column(db.String(), nullable=True)
    publish_date = db.Column(db.Date(), nullable=True)
    notice_type = db.Column(db.String(), nullable=True)
    notice_no = db.Column(db.String(), nullable=True)
    state = db.Column(db.String(), nullable=True)
    suburb = db.Column(db.String(), nullable=True)
    advertised = db.Column(db.String(), nullable=True)

class NoticeSchema(ma.ModelSchema):
    class Meta:
       model = Notice
    employee = ma.Nested(EmployeeSchema, only=("id", "first_name"))
    agency = ma.Nested(AgencySchema, only=("id", "title"))





#----------  USERS ----------


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	email = db.Column(db.String(120))
	password = db.Column(db.String())
	token = db.Column(db.String())
	admin = db.Column(db.Integer, nullable=True)
	supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=True)
	supplier = db.relationship("Supplier", backref="users")

class UserSchema(ma.ModelSchema):
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'email', 'token', 'admin', 'supplier')
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
import os
from flask import Flask, request, jsonify, Response, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_marshmallow import Marshmallow
import json
from datetime import datetime, date, time
from datetime import timedelta
import humanize
from flask_cors import CORS, cross_origin
import random, string

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
print(db)
from models import User, UserSchema, Comment, CommentSchema, Op, OpSchema, OpSimpleSchema, Unspsc, UnspscSchema, UnspscSchemaSimple, Agency, AgencySchema, Addenda, AddendaSchema, Contract, ContractSchema, Supplier, SupplierSchema, FilterUnspsc, FilterUnspscSchema, Page, Tag, Son, SonSchema, Employee, EmployeeSchema, Notice, NoticeSchema


# ---------------- LOAD SCHEMAS ---------------

user_schema = UserSchema()
users_schema = UserSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

op_schema = OpSchema()
ops_schema = OpSimpleSchema(many=True)

unspsc_schema = UnspscSchema()
unspscs_schema = UnspscSchema(many=True)

unspsc_simple_schema = UnspscSchemaSimple()
unspscs_simple_schema = UnspscSchemaSimple(many=True)

agency_schema = UnspscSchema()
agencies_schema = UnspscSchema(many=True)

addenda_schema = AddendaSchema()
addendas_schema = AddendaSchema(many=True)

contract_schema = ContractSchema()
contracts_schema = ContractSchema(many=True)

supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)

filterUnspsc_schema = FilterUnspscSchema()
filterUnspscs_schema = FilterUnspscSchema(many=True)

son_schema = SonSchema()
sons_schema = SonSchema(many=True)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

notice_schema = NoticeSchema()
notices_schema = NoticeSchema(many=True)




# ---------------- ROUTES ---------------

@app.route("/")
def hello():

    # check if the title is linked to any contracts where the unspsc_id==None
    contract_unspsc = Contract.query.filter_by(unspsc_id=None).all()
    result = contracts_schema.dump(contract_unspsc).data

    #for contract in result:
    #    temp_title = contract['category_temp_title'].capitalize()
    #    unspsc = Unspsc.query.filter_by(title=temp_title).all()
    #    result_unspsc = unspscs_schema.dump(unspsc).data
    #    for item in result_unspsc:
    #        new_unspsc_id = item['id']
    #        print(contract['id'])
    #        print(new_unspsc_id)
    #        print()  
    #        db.session.query(Contract).filter(Contract.id == contract['id']).\
    #            update({Contract.unspsc_id: new_unspsc_id}, synchronize_session=False)
    #        db.session.commit()            

    #        break


        


    #print(result[0])
    #jsonify(result)

    return jsonify(result)

    #db.session.query(Op).delete()
    #db.session.commit()

    #opportunity = Op.query.filter_by(id=240).first()
    #opportunity = Op.query.first()
    #opportunity.categories = []
    #opportunity.categories.remove(somecategory)
    #db.session.commit()
    #db.session.delete(opportunity)
    #db.session.commit()

    #db.create_all()

    #page = Page()
    #tag = Tag()
    #page.tags.append(tag)
    #db.session.add(page)

    #opportunity=Op.query.filter_by(id=240).first()
    #category = Unspsc.query.filter_by(id=224).first()
    #opportunity.categories.append(category)
    #db.session.add(opportunity)

    #db.session.commit()

    return "Hello World!!"

# ------------  FUNCTIONS ---------------

def api_response(message, data):
    # Formats the response for the API
    if data==None:
        response= {
            'message':message,
            'data': None,
            'status_code' : 200
        }
    else:
        response = {
            'message':message,
            'data': data,
            'status_code' : 200
        }
    return jsonify(response)



import hashlib, binascii, os

def hash_password(password):
    """Hash a password for storing."""
    h = hashlib.md5(password.encode())
    return h.hexdigest()



# ------------  LOGIN ---------------

@app.route("/login", methods=['POST'])
def login():

    data = request.form.to_dict()
    email = data['email']
    password = data['password']
    password = hash_password(password)
    try:
        print(email)
        user = User.query.filter_by(email=email).filter_by(password=password).first()
        result = user_schema.dumps(user).data
        if len(result)<=2:
            return api_response('Fail', result)
        else:
            return api_response('Success', result)
    except Exception as e:
	    return(str(e))



# ------------  USERS ---------------

@app.route("/users")
def users():
    try:
        users=User.query.all()
        result = users_schema.dump(users).data
        return jsonify(result)
    except Exception as e:
	    return(str(e))


@app.route("/user/<user_id>", methods=['GET'])
def user_detail(user_id):
    try:
        user = User.query.filter_by(id=user_id).all()
        result = users_schema.dumps(user).data
        return api_response('Success', result)
    except Exception as e:
	    return(str(e))


@app.route("/user/add", methods=['POST'])
def user_add():

    
    data = request.form.to_dict()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']

    token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    stored_password = hash_password(password)

    user = User.query.filter_by(email=email).first()
    result = user_schema.dumps(user).data
    if len(result)>2:
        return api_response('Error - email already exists', None)
    else:
        db.create_all()
        user = User(first_name=first_name, last_name=last_name, email=email, password=stored_password, token=token)
        db.session.add(user)
        db.session.commit()

        response = user_schema.dump(user).data
        return api_response('Success', response)



@app.route("/users/delete/<id_>")
def users_delete(id_):
    try:
        obj=User.query.filter_by(id=id_).one()
        db.session.delete(obj)
        db.session.commit()
        return "User deleted. user id={}".format(id_)
    except Exception as e:
	    return(str(e))




@app.route("/filter/unspsc/add", methods=['GET'])
@cross_origin()
def filter_unspsc_add():

    unspsc_id=request.args.get('unspsc_id')

    # Check the token matches the user ID, if not return empty results.
    user_id = request.args.get('id')
    token = request.args.get('token')
    user = User.query.filter_by(id=user_id).filter_by(token=token).first()
    result = user_schema.dumps(user).data
    if len(result)<=2:
        output = {"results": []}
        return jsonify(output)  
    else:
        db.create_all()
        filter_ = FilterUnspsc(user_id=user_id, unspsc_id=unspsc_id)
        db.session.add(filter_)
        db.session.commit()

        response = filterUnspsc_schema.dump(filter_).data
        return api_response('Success - Added Filter', response)




# ------------  OPPORTUNITIES ---------------

@app.route("/op", methods=['GET'])
def op():
    page = request.args.get('page', 1, type=int)
    filter_results = request.args.get('filter', 1, type=int)

    # Check the token matches the user ID, if not return empty results.
    user_id = request.args.get('id')
    token = request.args.get('token')
    user = User.query.filter_by(id=user_id).filter_by(token=token).first()
    result = user_schema.dumps(user).data
    if len(result)<=2:
        output = {"results": []}
        return jsonify(output)


    unspsc_filters = []

    # find all the UNSPSC filters
    myfilter = FilterUnspsc.query.filter_by(user_id=user_id).all()
    unspsc_filters_result = filterUnspscs_schema.dumps(myfilter).data
    unspsc_filters_result = json.loads(unspsc_filters_result)

    #print("************")
    #print(unspsc_filters_result)

    for item in unspsc_filters_result:
        unspsc_filters.append( item['unspsc']['id'] ) 

    #print("************")
    #print(unspsc_filters)


    try:
        # Only show the open opportunities
        opportunities = Op.query #.all() #session.query(Contract)
        opportunities = opportunities.filter( getattr(Op,'close_date')>=datetime.now()-timedelta(days=1) )
        #for item in unspsc_filters:
        #opportunities = opportunities.filter(Op.categories.any(Unspsc.id == 1))   
        opportunities = opportunities.paginate(page, 500, False)


        next_url = url_for('op', page=opportunities.next_num) \
            if opportunities.has_next else None
        prev_url = url_for('op', page=opportunities.prev_num) \
            if opportunities.has_prev else None
        total = opportunities.total
        pages = opportunities.pages

        output = {}
        output['pagination'] = {"next_url":next_url, "prev_url":prev_url, "total":total, "pages":pages}
        output['results_raw'] = ops_schema.dump(opportunities.items).data

        #print(result)

        output['results'] = []
        # Update all of the times to human readable
        for op in output['results_raw']:
            hide_op = False
            published = datetime.strptime(op['publish_date'], '%Y-%m-%d')
            #print(humanize.naturalday(published))
            op['published_date_human'] = humanize.naturalday(published)
            close_date = datetime.now() - datetime.strptime(op['close_date'], '%Y-%m-%d')
            op['close_date_human'] = humanize.naturaltime(close_date)
            op['title'] = op['title'].capitalize()

            for category in op['categories']:
                if category['id'] in unspsc_filters:
                    hide_op = True
                highest_level = 0
                if category['level_int']>highest_level:
                    op['category_title'] = category['title'].capitalize()
                    op['category_id'] = category['id']

            if hide_op==False:
                output['results'].append(op)
            

        return jsonify(output)


    except Exception as e:
	    return(str(e))



@app.route("/op/<op_id>", methods=['GET'])
def op_detail(op_id):
    
    try:
        opportunity = Op.query.filter_by(id=op_id).first()
        result = op_schema.dumps(opportunity).data
        result = json.loads(result)

        published = datetime.now() - datetime.strptime(result['publish_date'], '%Y-%m-%d')
        result['published_date_human'] = humanize.naturaltime(published)
        close_date = datetime.now() - datetime.strptime(result['close_date'], '%Y-%m-%d')
        result['close_date_human'] = humanize.naturaltime(close_date)

        # Loop through and add the categories to segment/class etc.
        result['unspsc_segment'] = None
        result['unspsc_family'] = None
        result['unspsc_class'] = None
        result['unspsc_commodity'] = None
        for category in result['categories']:
            if category['level_int']==1:
                result['unspsc_segment'] = category
            elif category['level_int']==2:
                result['unspsc_family'] = category
            elif category['level_int']==3:
                result['unspsc_class'] = category
            elif category['level_int']==4:
                result['unspsc_commodity'] = category
        
        result['panel_arrangement'] = 'Yes' if result['panel_arrangement'] == 1 else 'No'
        result['multi_stage'] = 'Yes' if result['multi_stage'] == 1 else 'No'
        result['multi_agency_access'] = 'Yes' if result['multi_agency_access'] == 1 else 'No'
        
        return result


    except Exception as e:
	    return(str(e))


@app.route("/op/add", methods=["POST"])
def op_add():
    try:
        data = request.form.to_dict()
        atm_id = data['atm_id']
        unspsc = data['unspsc']

        
        title = data['title']
        atm_id = data['atm_id']
        description = data['description']
        atm_type = data['atm_type']
        publish_date = data['publish_date']
        close_date = data['close_date']
        conditions_for_participation = data['conditions_for_participation']
        panel_arrangement = data['panel_arrangement']
        timeframe_for_delivery = data['timeframe_for_delivery']
        multi_stage = data['multi-stage']
        multi_agency_access = data['multi_agency_access']
        address_for_lodgement = data['address_for_lodgement']
        agency_id = data['agency_id']
        document_link = data['document_link']
        #estimated_value = db.Column(db.String()) #estimated_value_(aud)
        #location = db.Column(db.String()) ## NEEDS WORK act, nsw, vic, sa, wa, qld, nt, tas"
        #addenda_available = data['addenda_available']  #NEEDS WORK
        
        

        obj=Op.query.filter_by(atm_id=atm_id).first()
        if obj==None:
            #db.session.add(opportunity)
            #data = opportunity
            #db.session.add(comment)

            db.create_all()
            opportunity = Op(title=title, atm_id=atm_id, description=description, atm_type=atm_type, publish_date=publish_date, close_date=close_date, agency_id=agency_id, conditions_for_participation=conditions_for_participation, panel_arrangement=panel_arrangement, timeframe_for_delivery=timeframe_for_delivery, multi_stage=multi_stage, multi_agency_access=multi_agency_access, address_for_lodgement=address_for_lodgement, document_link=document_link)
            category = Unspsc.query.filter_by(unspsc=unspsc).first()
            opportunity.categories.append(category)

            # Loop through and add all of the categories
            unspsc_complete = False
            while unspsc_complete==False:
                if category.parent_id!=0:
                    category = Unspsc.query.filter_by(id=category.parent_id).first()
                    opportunity.categories.append(category)
                    if category.parent_id==0:
                        unspsc_complete=True

                    db.session.add(opportunity)
                    db.session.commit()
                else:
                    unspsc_complete=True

            response = op_schema.dump(opportunity).data
            return api_response('Success - Added Opportunity', response)
        else:
            # UPDATE ANY CHANGES TO THE OPPORTUNITY
            obj.document_link = document_link
            db.session.commit()

            return api_response('Success - Opportunity Already Exists', None)
    except Exception as e:
	    return(str(e))



@app.route("/op/delete/<id_>")
def opportunities_delete(id_):
    try:
        obj=Op.query.filter_by(id=id_).one()
        db.session.delete(obj)
        db.session.commit()
        return api_response('Success - Opportunity Deleted', None)
    except Exception as e:
	    return(str(e))



# ------------  ADDENDA ---------------

@app.route("/addenda")
def addenda():
    try:
        addenda=Addenda.query.all()
        result = addendas_schema.dump(addenda).data
        return jsonify(result)
    except Exception as e:
	    return(str(e))


@app.route("/addenda/<addenda_id>", methods=['GET'])
def addenda_detail(addenda_id):
    try:
        addenda = Addenda.query.filter_by(id=addenda_id).all()
        result = addenda_schema.dumps(addenda).data
        return json.loads(result)
    except Exception as e:
	    return(str(e))


@app.route("/addenda/add", methods=['GET'])
def addenda_add():

    title=request.args.get('title')
    #published=request.args.get('published')
    published = datetime.datetime.now()
    
    db.create_all()
    addenda = Addenda(title=title, published=published)
    db.session.add(addenda)
    db.session.commit()

    response = addenda_schema.dump(addenda).data
    return api_response('Success - Added Addenda', response)



# ------------  CONTRACTS ---------------

@app.route("/contracts", methods=['GET'])
def contracts():
    page = request.args.get('page', 1, type=int)
    paginate = request.args.get('paginate', "yes", type=str)
    display = request.args.get('display', 'filtered', type=str)

    #x = datetime.now()
    #date_end = x.strftime("%Y-%m-%d")
    date_end = request.args.get('date_end', None, type=str)
    date_start = request.args.get('date_start', None, type=str)
    agency_id = request.args.get('agency_id', None, type=int)
    supplier_id = request.args.get('supplier_id', None, type=int)


    filters = []

    # Builds the filter string
    if date_end!=None:
        filters.append({'field': 'contract_start', 'operator': "<=", 'value': date_end})
    if date_start!=None:
        filters.append({'field': 'contract_start', 'operator': ">=", 'value': date_start})
    if agency_id!=None:
        filters.append({'field': 'agency_id', 'operator': "==", 'value': agency_id})
    if supplier_id!=None:
        filters.append({'field': 'supplier_id', 'operator': "==", 'value': supplier_id})
    
    #filters = [
    #    {'field': 'contract_duration', 'operator': "==", 'value': 210},
    #    {'field': 'contract_start', 'operator': ">=", 'value': date_start},
    #    {'field': 'contract_start', 'operator': "<=", 'value': date_end}
    #    ]

    query = Contract.query #.all() #session.query(Contract)
    for item in filters:
        if item['operator']=="==":
            query = query.filter( getattr(Contract,item['field'])==item['value'] )
        elif item['operator']==">=":
            query = query.filter( getattr(Contract,item['field'])>=item['value'] )
        elif item['operator']=="<=":
            query = query.filter( getattr(Contract,item['field'])<=item['value'] )
        elif item['operator']=="!=":
            query = query.filter( getattr(Contract,item['field'])!=item['value'] )
    # now we can run the query
    query = query.order_by(desc(Contract.publish_date))

    output = {}

    if paginate=="yes":
        contracts = query.paginate(page, 1000, False)

        next_url = url_for('contracts', page=contracts.next_num) \
            if contracts.has_next else None
        prev_url = url_for('contracts', page=contracts.prev_num) \
            if contracts.has_prev else None
        total = contracts.total
        pages = contracts.pages

        output['pagination'] = {"next_url":next_url, "prev_url":prev_url, "total":total, "pages":pages}
        output['results'] = contracts_schema.dump(contracts.items).data
    else:
        contracts = query.all()
        output['results'] = contracts_schema.dump(contracts).data
    

    #print(output['results'])
    
    #try:
    # Format all of the dates and values
    newest_contract = datetime.now()-timedelta(days=10000) #datetime.strptime(datetime.now(), '%Y-%m-%d')
    oldest_contract = datetime.now() #datetime.strptime(datetime.now(), '%Y-%m-%d')
    for item in output['results']:
        
        published = datetime.strptime(item['publish_date'], '%Y-%m-%d')
        if newest_contract<published:
            newest_contract = published
        if oldest_contract>published:
            oldest_contract = published

        item['contract_open'] = "finished"
        try:
            item['contract_value'] = round(float(item['contract_value']))
            value = float(item['contract_value'])
            if value<1000000:
                item['contract_value_human'] = humanize.intcomma(int(value))
            else:
                item['contract_value_human'] = humanize.intword(int(value))
        except:
            item['contract_value_human'] = item['contract_value']
            item['contract_value'] = 0

        #published = datetime.now() - datetime.strptime(result['publish_date'], '%Y-%m-%d')
        x = datetime.strptime(item['contract_start'], '%Y-%m-%d')
        start_year = x.strftime("%Y")
        y = datetime.strptime(item['contract_end'], '%Y-%m-%d')
        end_year = y.strftime("%Y")
        item['contract_start_human'] = x.strftime("%b %d %Y")
        item['contract_end_human'] = y.strftime("%b %d %Y")
        if (y<datetime.now()+timedelta(days=30)) and (y>datetime.now()):
            item['contract_open'] = "ending soon"
        elif y>datetime.now():
            item['contract_open'] = "ongoing"

    output['data'] = {}

    output['data']['newest_contract'] = newest_contract.strftime("%b %d %Y")
    output['data']['oldest_contract'] = oldest_contract.strftime("%b %d %Y")


    return jsonify(output)

    #except Exception as e:
	#    return(str(e))


@app.route("/contract/add", methods=["POST"])
def contract_add():

    data = request.form.to_dict()
    #print(data)
    title = data['title']
    cn_id = data['cn_id']
    contract_start =  data['contract_start']
    contract_end =  data['contract_end']
    contract_duration =  data['contract_duration']

    if 'confidentiality_contract' in data:
        confidentiality_contract = data['confidentiality_contract']
    else:
        confidentiality_contract = "No"

    if 'agency_reference_id' in data:
        agency_reference_id = data['agency_reference_id']
    else:
        agency_reference_id = None

    if 'confidentiality_outputs' in data:
        confidentiality_outputs = data['confidentiality_outputs']
    else:
        confidentiality_outputs = "No"

    contract_value = data['contract_value']
    procurement_method = data['procurement_method']
    description = data['description']
    publish_date = data['publish_date']
    category_temp_title = data['category']
    agency_id = data['agency_id']
    supplier_id = data['supplier_id']

    if 'son_id_actual' in data:
        son_id = data['son_id_actual']
    else:
        son_id = None

    if 'atm_id' in data:
        atm_id = data['atm_id']
    else:
        atm_id = None

    contract=Contract.query.filter_by(cn_id=cn_id).first()
    if contract==None:
        db.create_all()
        contract = Contract(title=title, cn_id=cn_id, son_id=son_id, atm_austender_id=atm_id, contract_start=contract_start, contract_end=contract_end, contract_duration=contract_duration, category_temp_title=category_temp_title, agency_id=agency_id, confidentiality_contract=confidentiality_contract, agency_reference_id=agency_reference_id, confidentiality_outputs=confidentiality_outputs, contract_value=contract_value, procurement_method=procurement_method, description=description, publish_date=publish_date, supplier_id=supplier_id)
        db.session.add(contract)
        db.session.commit()
    else:
        # UPDATE ANY CHANGES TO THE OPPORTUNITY
        contract.son_id = son_id
        contract.atm_austender_id = atm_id
        db.session.commit()

    response = contract_schema.dump(contract).data
    return contract



@app.route("/contract/<contract_id>", methods=['GET'])
def contract_detail(contract_id):
    try:
        contract = Contract.query.filter_by(id=contract_id).first()
        result = contract_schema.dumps(contract).data

        #result['contract_value_human'] = humanize.naturaltime(result['contract_value'])

        return json.loads(result)
    except Exception as e:
	    return(str(e))



@app.route("/contract/unspsc")
def contract_unspsc():
    # Shows all of the contracts that need to have the UNSPSC linked by the spider.
    try:  

        contract_unspsc = Contract.query.filter_by(unspsc_id = None).all()
        result = contracts_schema.dump(contract_unspsc).data  

        # Loop through and update from the UNSPSC database
        for item in result:
            print(item['category_temp_title'])

            obj = Unspsc.query #.all() #session.query(Contract)
            obj = obj.filter(Unspsc.title.ilike(item['category_temp_title']))
            obj = obj.first()

            if obj!=None:
                temp_result = unspsc_schema.dump(obj).data 
                #print(temp_result)
                #print(item['id'])
                
                contract_obj = Contract.query.filter_by(id = item['id']).first()
                contract_obj.unspsc_id = temp_result['id']
                db.session.commit()
            

        # reload and only show the ones that need scraping form the unspsc site.
        contract_unspsc = Contract.query.filter_by(unspsc_id = None).all()
        result = contracts_schema.dump(contract_unspsc).data 

        results_distinct = []
        searched_text = []
        for item in result:
            if item['category_temp_title'] in searched_text:
                pass
            else:
                searched_text.append(item['category_temp_title'])
                results_distinct.append({"category_temp_title":item['category_temp_title'], "id":item['id']})


        return jsonify(results_distinct)
    except Exception as e:
	    return(str(e))



# ------------  SON ---------------

@app.route("/son/add", methods=['GET'])
def son_add():

    austender_id=request.args.get('austender_id').upper()
    austender_link=request.args.get('austender_link')
    
    son = Son.query.filter_by(austender_link=austender_link).first()
    if son==None:
        db.create_all()
        son = Son(austender_id=austender_id, austender_link=austender_link)
        db.session.add(son)
        db.session.commit()

        response = son_schema.dump(son).data
        return api_response('Success - Son Added', response)
    else:
        response = son_schema.dump(son).data
        return api_response('Success - Son Already Exists', response)





# ------------  UNSPSC ---------------

@app.route("/unspsc")
def unspsc():
    try:
        filter_null = bool(request.args.get('filter_scraped'))
        filter_ = request.args.get('filter')
        if filter_null==True:
            # only show results that have a null title
            unspsc=Unspsc.query.filter_by(scraped=0).all()
        else:
            if filter_=="segment":
                unspsc = Unspsc.query.filter_by(level=filter_).order_by(Unspsc.title).all()
            else:
                unspsc = Unspsc.query.all()

        result = unspscs_schema.dump(unspsc).data  # THIS SHOWS ALL OF THE Ops FOR THE UNSPSCs
        #result = unspscs_simple_schema.dump(unspsc).data
        return json.dumps(result)
        #return jsonify(result)
    except Exception as e:
	    return(str(e))


@app.route("/unspsc/<unspsc_id>", methods=['GET'])
def unspsc_detail(unspsc_id):
    #try:
    unspsc = Unspsc.query.filter_by(id=unspsc_id).first()
    result = unspsc_schema.dumps(unspsc).data
    result = json.loads(result)

    unspsc = Unspsc.query.filter_by(parent_id=unspsc_id).order_by(Unspsc.title).all()
    children = unspscs_schema.dump(unspsc).data
    result['children'] = children
    
    return result

    #except Exception as e:
	#    return(str(e))



def update_contract_unspsc():
    # check if the title is linked to any contracts where the unspsc_id==None
    contract_unspsc = Contract.query.filter_by(unspsc_id=None).all()
    result = contracts_schema.dump(contract_unspsc).data

    for contract in result:
        temp_title = contract['category_temp_title'].capitalize()
        unspsc = Unspsc.query.filter_by(title=temp_title).all()
        result_unspsc = unspscs_schema.dump(unspsc).data
        for item in result_unspsc:
            new_unspsc_id = item['id']
            print(contract['id'])
            print(new_unspsc_id)
            print()  
            db.session.query(Contract).filter(Contract.id == contract['id']).\
                update({Contract.unspsc_id: new_unspsc_id}, synchronize_session=False)
            db.session.commit()            
            break




@app.route("/unspsc/add/<unspsc>/<title_>")
def unspsc_add(unspsc, title_):
    try:
        obj=Unspsc.query.filter_by(unspsc=unspsc).first()
        if obj==None:

            segment_ = str(unspsc)[:-6] + "000000"
            family_ = str(unspsc)[:-4] + "0000"
            class_ = str(unspsc)[:-2] + "00"
            commodity_ = str(unspsc)

            output = {
                1:{'level':'segment', 'level_int':1, 'unspsc':segment_, 'parent':0},
                2:{'level':'family', 'level_int':2, 'unspsc':family_, 'parent':segment_},
                3:{'level':'class', 'level_int':3, 'unspsc':class_, 'parent':family_},
                4:{'level':'commodity', 'level_int':4, 'unspsc':commodity_, 'parent':class_}
                }

            for key, value in output.items():

                if value['level']!="segment": 
                    obj=Unspsc.query.filter_by(unspsc=value['parent']).first()
                    parent_id = obj.id
                else:
                    parent_id=0

                obj_temp=Unspsc.query.filter_by(unspsc=value['unspsc']).first()
                if obj_temp==None:
                    db.create_all()
                    unspsc = Unspsc(unspsc=value['unspsc'], title=title_, level=value['level'], level_int=value['level_int'], parent_id=parent_id)
                    db.session.add(unspsc)
                    db.session.commit()

            update_contract_unspsc()
            return api_response('Success - All unspscs Added', None)
        else:
            update_contract_unspsc()
            return api_response('Success - unspsc Already Exists', None)


    except Exception as e:
	    return(str(e))


@app.route("/unspsc/title")
def unspsc_title():
    try:
        title = request.args.get('title').capitalize()
        unspsc = request.args.get('unspsc')

        db.session.query(Unspsc).filter(Unspsc.unspsc == unspsc).\
            update({Unspsc.title: title, Unspsc.scraped: 1}, synchronize_session=False)
        db.session.commit()
        return api_response('Success - UNSPSC title updated', None)

    except Exception as e:
	    return(str(e))



@app.route("/unspsc/parents/<unspsc_id>")
def unspsc_parents(unspsc_id):
    try:
        output = {}
        unspsc_search = True # continue to loop through and search all children
        unspsc=Unspsc.query.filter_by(id=unspsc_id).first()
        if unspsc!=None:
            # Loop through all of the parent UNSPSCs
            output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id, 'level_int':unspsc.level_int}
            while unspsc_search==True:
                if unspsc.parent_id!=0:
                    unspsc=Unspsc.query.filter_by(id=unspsc.parent_id).one()
                    output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id, 'level_int':unspsc.level_int}
                else:
                    unspsc_search = False
        else:
            output = {'response': False}
        return jsonify(output)
    except Exception as e:
	    return(str(e))



@app.route("/unspsc/children/<unspsc_id>")
def unspsc_children(unspsc_id):
    
    try:
        unspsc = Unspsc.query.filter_by(parent_id=unspsc_id).all()
        result = unspscs_schema.dump(unspsc).data
        result = jsonify(result)
        return result

    except Exception as e:
        return(str(e))


# ------------  AGENCIES ---------------

@app.route("/agencies")
def agencies():
    try:
        agencies=Agency.query.all()
        result = agencies_schema.dump(agencies).data
        return jsonify(result)
    except Exception as e:
	    return(str(e))


@app.route("/agency/<agency_id>", methods=['GET'])
def agency_detail(agency_id):
    try:
        agency = Agency.query.filter_by(id=agency_id).first()
        result = agency_schema.dumps(agency).data
        return json.loads(result)
    except Exception as e:
	    return(str(e))


@app.route("/agency/add", methods=['GET'])
def agency_add():

    title=request.args.get('title').capitalize()
    portfolio=request.args.get('portfolio').capitalize()
    if portfolio=="":
        portfolio = None
    
    agency = Agency.query.filter_by(title=title).first()
    if agency==None:
        db.create_all()
        agency = Agency(title=title, portfolio=portfolio)
        db.session.add(agency)
        db.session.commit()

        response = agency_schema.dump(agency).data
        return api_response('Success - Agency Added', response)
    else:
        agency.portfolio = portfolio
        db.session.commit()

        response = agency_schema.dump(agency).data
        return api_response('Success - Agency Already Exists', response)



# ------------  SUPPLIERS ---------------

@app.route("/suppliers")
def suppliers():
    try:
        suppliers=Supplier.query.all()
        result = suppliers_schema.dump(suppliers).data
        return jsonify(result)
    except Exception as e:
	    return(str(e))


@app.route("/suppliers/add", methods=['GET'])
def suppliers_add():

    name=request.args.get('name').capitalize()
    abn=request.args.get('abn')
    country=request.args.get('country')
    try:
        country = country.capitalize()
    except:
        pass
    
    supplier = Supplier.query.filter_by(abn=abn).first()
    if supplier==None:
        db.create_all()
        supplier = Supplier(name=name, abn=abn, country=country)
        db.session.add(supplier)
        db.session.commit()

        response = supplier_schema.dump(supplier).data
        return api_response('Success - Supplier Added', response)
    else:
        response = supplier_schema.dump(supplier).data
        return api_response('Success - Supplier Already Exists', response)


@app.route("/supplier/<supplier_id>", methods=['GET'])
def supplier_detail(supplier_id):
    try:
        supplier = Supplier.query.filter_by(id=supplier_id).first()
        result = supplier_schema.dumps(supplier).data
        return json.loads(result)
    except Exception as e:
	    return(str(e))





# ------------  APS EMPLOYEE ---------------
@app.route("/employee/add", methods=['POST'])
def employee_add():

    data = request.form.to_dict()
    print(data)
    first_name = data['employee_first_name']
    last_name = data['employee_last_name']
    employee_no = data['employee_no']
    gender = data['gender']

    employee = Employee.query.filter_by(employee_no=employee_no).first()
    result = employee_schema.dumps(employee).data
    if len(result)>2:
        return api_response('User already exists', result)
    else:
        db.create_all()
        employee = Employee(first_name=first_name, last_name=last_name, employee_no=employee_no, gender=gender)
        db.session.add(employee)
        db.session.commit()

        response = employee_schema.dump(employee).data
        return api_response('Success', response)



#{'employee_first_name': u'Karen-Maree', 'agency_notice': u'Department of health', 'notice_no': u'10741900', u'classification': u'APS Level 6', u'advertised': u'10736497: PS42-Thu, Thursday, 18 October 2018', u'agency_employment_act': u'PS Act 1999', u'agency': u'Department of Health', 'employee_no': u'608-76477', 'notice_type': u'Promotion', 'employee_last_name': u'Garside', 'classification_from': u'APS Level 5', u'location': u'Parramatta - NSW', u'position_details': u'Senior Investigator,  Investigation Section', u'position': u'18-PBID-2028', 'portfolio': u'health'}

# ------------  APS EMPLOYEE ---------------
@app.route("/notice/add", methods=['POST'])
def notice_add():

    data = request.form.to_dict()
    print(data)
    notice_no = data['notice_no']
    
    try:
        employee_id = data['employee_id']
    except:
        employee_id = None

    notice_type = data['notice_type']

    try:
        agency_id = data['agency_id']
    except:
        agency_id = None

    try:
        classification_from = data['classification_from']
    except:
        classification_from=None

    try:
        classification = data['classification']
    except:
        classification=None

    try:
        position = data['position']
    except:
        position=None

    try:
        position = data['position']
    except:
        position=None

    try:
        advertised = data['advertised']
    except:
        advertised=None


    published = datetime.strptime(data['published'], '%d %b %Y')
    #published = published.strftime("%Y-%d-%m")
    
    try:
        position_details = data['position_details']
    except:
        position_details=None

    try:
        state = data['state']
    except:
        state=None
    
    try:
        suburb = data['suburb']
    except:
        suburb=None


    notice = Notice.query.filter_by(notice_no=notice_no).first()
    result = notice_schema.dumps(notice).data
    if len(result)>2:
        return api_response('notice already exists', result)
    else:
        db.create_all()
        notice = Notice(publish_date=published, advertised=advertised, position_details=position_details, state=state, suburb=suburb, agency_id=agency_id, notice_no=notice_no, employee_id=employee_id, notice_type=notice_type, classification_from=classification_from, classification=classification, position=position)
        db.session.add(notice)
        db.session.commit()

        response = notice_schema.dump(notice).data
        return api_response('Success', response)








@app.route("/unspsc/delete/<id_>")
def unspsc_delete(id_):
    try:
        if str(id_)=='all':
            db.session.query(Unspsc).delete()
        else:
            obj=Unspsc.query.filter_by(id=id_).one()
            db.session.delete(obj)

        db.session.commit()
        return "Unspsc deleted. Unspsc id={}".format(id_)
    except Exception as e:
	    return(str(e))





if __name__ == '__main__':
    app.run()
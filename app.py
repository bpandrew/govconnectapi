import os
import requests 
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_marshmallow import Marshmallow
import json
from datetime import datetime, date, time, timedelta
import humanize
from flask_cors import CORS, cross_origin
import random, string
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import functions # import all of the custom written functions
import charts


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
ma = Marshmallow(app)
# import all of the database models and schemas
from models import User, UserSchema, Comment, CommentSchema, Op, OpSchema, OpSimpleSchema, Unspsc, UnspscSchema, UnspscSchemaSimple, Agency, AgencySchema, Addenda, AddendaSchema, Contract, ContractSchema, Supplier, SupplierSchema, FilterUnspsc, FilterUnspscSchema, Page, Tag, Son, SonSchema, Employee, EmployeeSchema, Notice, NoticeSchema, Division, DivisionSchema, Branch, BranchSchema


# ------------------------------------ LOGIN / LOGOUT ------------------------------------
# ----------------------------------------------------------------------------------------

@app.route("/cache")
def cache():
    return str(datetime.now())


# --- LANDING PAGE ---
@app.route("/")
def hello():
    return render_template('index.html')


# --- LOGIN PAGE ---
from forms import LoginForm
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Load the form
    form = LoginForm()
    # Check for errors
    data = {}
    data['error'] = request.args.get('error')
    if form.validate_on_submit():
        # hash the password
        password = functions.hash_password(form.password.data)

        obj = User.query.filter_by(email=form.email.data).filter_by(password=password).first()
        result = json.loads(UserSchema().dumps(obj).data)
        if obj!=None:
            session['first_name'] = result['first_name']
            session['user_id'] = result['id']
            session['user_token'] = result['token']
            return redirect(url_for('op'))
        else:
            return redirect(url_for('login')+"?error=1")

    return render_template('login.html', form=form, data=data)


# --- LOGOUT PAGE ---
@app.route("/logout")
def logout():
    session['first_name'] = None
    session['user_id'] = None
    session['user_token'] = None
    return redirect(url_for('login'))


# ----------------------------------------- USERS ----------------------------------------
# ----------------------------------------------------------------------------------------

from forms import AddUser

@app.route('/user/add', methods=['GET', 'POST'])
def user_add():
    # Load the form
    form = AddUser()
    data = {}
    data['error'] = request.args.get('error')

    if form.validate_on_submit():
        # Add the User
        token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        stored_password = functions.hash_password(form.password.data) # Has the password

        user = User.query.filter_by(email=form.email.data).first()
        result = UserSchema().dumps(user).data
        if user!=None:
            return redirect(url_for('user_add')+"?error=1")
        else:
            db.create_all()
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=stored_password, token=token)
            db.session.add(user)
            db.session.commit()
            result = UserSchema().dump(user).data
            
            session['first_name'] = result['first_name']
            session['user_id'] = result['id']
            session['user_token'] = result['token']
            return redirect(url_for('op'))

    return render_template('register.html', form=form, data=data)




# ------------------------------------- OPPORTUNITIES ------------------------------------
# ----------------------------------------------------------------------------------------

@app.route("/op", methods=['GET'])
def op():
    try:
        functions.login_required(session['user_token']) # confirm the user is logged in
    except:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    filter_results = request.args.get('filter', 1, type=int)

    # find all the UNSPSC filters for the user
    unspsc_filters = []
    myfilter = FilterUnspsc.query.filter_by(user_id=session['user_id']).all()
    unspsc_filters_result = FilterUnspscSchema(many=True).dumps(myfilter).data
    unspsc_filters_result = json.loads(unspsc_filters_result)
    for item in unspsc_filters_result:
        unspsc_filters.append( item['unspsc']['id'] ) 
    print(unspsc_filters)

    opportunities = Op.query
    opportunities = opportunities.filter( getattr(Op,'close_date')>=datetime.now()-timedelta(days=1) ) # Only show the open opportunities
    opportunities = opportunities.all() #.paginate(page, 100, False)
 
    output = {}
    output['results_raw'] = OpSimpleSchema(many=True).dump(opportunities).data
    output['results'] = []

    # Update all of the times to human readable # THIS MAY BE ABLE TO BE DONE IS JS CLIENT SIDE - TO AVOID THIS LOOP?
    for op in output['results_raw']:
        published = datetime.strptime(op['publish_date'], '%Y-%m-%d')
        op['published_date_human'] = humanize.naturalday(published)
        close_date = datetime.now() - datetime.strptime(op['close_date'], '%Y-%m-%d')
        op['close_date_human'] = humanize.naturaltime(close_date)
        op['title'] = op['title'].capitalize()
        op['category_display'] = max(op['categories'], key=lambda x:x['level_int']) # Get the highest (most specific) category provided for the ATM
        output['results'].append(op)
        
    return render_template('opportunities.html', data=output)




@app.route("/op/<op_id>", methods=['GET'])
def op_detail(op_id):
    try:
        opportunity = Op.query.filter_by(id=op_id).first()
        result = OpSchema().dumps(opportunity).data
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
        
        #return result

        return render_template('opportunity.html', data=result)

    except Exception as e:
	    return(str(e))



@app.route("/op/add", methods=["POST"])
def op_add():
    try:
        data = request.form.to_dict() # Transofrm the POST data into a dictionary

        obj=Op.query.filter_by(atm_id=atm_id).first()
        if obj==None:
            db.create_all()
            opportunity = Op(title=data['title'], atm_id=data['atm_id'], description=data['description'], atm_type=data['atm_type'], publish_date=data['publish_date'], close_date=data['close_date'], agency_id=data['agency_id'], conditions_for_participation=data['conditions_for_participation'], panel_arrangement=data['panel_arrangement'], timeframe_for_delivery=data['timeframe_for_delivery'], multi_stage=data['multi-stage'], multi_agency_access=data['multi_agency_access'], address_for_lodgement=data['address_for_lodgement'], document_link=data['document_link'])
            category = Unspsc.query.filter_by(unspsc=data['unspsc']).first()
            opportunity.categories.append(category)

            # Loop through and add all of the parent/child categories
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

            response = OpSchema().dump(opportunity).data
            return functions.json_response('Success - Added Opportunity', response)
        else:
            response = OpSchema().dump(obj).data # get the existing op data
            # Update any changes to the opportunity
            obj.document_link = document_link
            db.session.commit()

            return functions.json_response('Success - Opportunity Already Exists', response)
    except Exception as e:
	    return(str(e))



# ----------------------------------------- CONTRACTS ----------------------------------------
# --------------------------------------------------------------------------------------------



@app.route("/contracts", methods=['GET'])
def contracts(supplier_id=None):
    try:
        functions.login_required(session['user_token']) # confirm the user is logged in
    except:
        return redirect(url_for('login'))

    page = request.args.get('page', 0, type=int)
    paginate = request.args.get('paginate', "yes", type=str)
    display = request.args.get('display', 'filtered', type=str)

    date_end = request.args.get('date_end', None, type=str)
    date_start = request.args.get('date_start', None, type=str)
    agency_id = request.args.get('agency_id', None, type=int)

    output = {}

    if display.lower()!="search":
        d = datetime.now()
        d = d-timedelta(days=(page*7))
        week_start = d-timedelta(days=d.weekday())
        start_date_human = week_start.strftime("%a %d %b")
        publish_date_start = week_start.strftime("%Y-%m-%d")
        publish_date_end = week_start+timedelta(days=6)
        end_date_human = publish_date_end.strftime("%a %d %b \'%y")
        #print(start_date, end_date)
        output['data'] = {}
        output['data']['newest_contract'] = end_date_human
        output['data']['oldest_contract'] = start_date_human

    filters = []
    # Builds the filter string
    if publish_date_end!=None:
        filters.append({'field': 'publish_date', 'operator': "<=", 'value': publish_date_end})
    if publish_date_start!=None:
        filters.append({'field': 'publish_date', 'operator': ">=", 'value': publish_date_start})
    if date_end!=None:
        filters.append({'field': 'contract_start', 'operator': "<=", 'value': date_end})
    if date_start!=None:
        filters.append({'field': 'contract_start', 'operator': ">=", 'value': date_start})
    if agency_id!=None:
        filters.append({'field': 'agency_id', 'operator': "==", 'value': agency_id})
    if supplier_id!=None:
        filters.append({'field': 'supplier_id', 'operator': "==", 'value': supplier_id})
    
    query = Contract.query
    for item in filters:
        if item['operator']=="==":
            query = query.filter( getattr(Contract,item['field'])==item['value'] )
        elif item['operator']==">=":
            query = query.filter( getattr(Contract,item['field'])>=item['value'] )
        elif item['operator']=="<=":
            query = query.filter( getattr(Contract,item['field'])<=item['value'] )
        elif item['operator']=="!=":
            query = query.filter( getattr(Contract,item['field'])!=item['value'] )
    # Run the query with the filter
    query = query.order_by(desc(Contract.publish_date))

    next_url = url_for('contracts', page=page+1)
    prev_url = url_for('contracts', page=page-1)
    output['pagination'] = {"next_url":next_url, "prev_url":prev_url, "current":page}
    contracts = query.all()
    output['results'] = ContractSchema(many=True).dump(contracts).data
   
    # Format all of the dates and values
    for item in output['results']:
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

    return render_template('contracts.html', data=output)



@app.route("/contract/<contract_id>", methods=['GET'])
def contract_detail(contract_id):

	contract = Contract.query.filter_by(id=contract_id).first()
	data = ContractSchema().dumps(contract).data
	data = json.loads(data)
	data['contract_open'] = "FINISHED"
	x = datetime.strptime(data['contract_start'], '%Y-%m-%d')
	start_year = x.strftime("%Y")
	y = datetime.strptime(data['contract_end'], '%Y-%m-%d')
	end_year = y.strftime("%Y")
	data['contract_start_human'] = x.strftime("%b %d %Y")
	data['contract_end_human'] = y.strftime("%b %d %Y")
	# create the closing text
	if y>datetime.now():
		data['contract_closing'] = "will end " + humanize.naturaltime(y)
	else:
		data['contract_closing'] = "ended " + humanize.naturaltime(y)
		
	if (y<datetime.now()+timedelta(days=30)) and (y>datetime.now()):
		data['contract_open'] = "ENDING SOON"
	elif y>datetime.now():
		data['contract_open'] = "ONGOING"
		
	contract_data = data.copy()
	
	contract = Contract.query.filter_by(supplier_id=contract_data['supplier']['id']).all()
	contracts = ContractSchema(many=True).dumps(contract).data
	contracts = json.loads(contracts)
	
	contracts = json_normalize(contracts)
	
	cfy_start, cfy_end, lfy_start, lfy_end, now_string = functions.financial_years()
	cfy = contracts[contracts['contract_start']>=cfy_start]
	cfy = cfy[cfy['contract_start']<=cfy_end]
	lfy = contracts[contracts['contract_start']>=lfy_start]
	lfy = lfy[lfy['contract_start']<=lfy_end]
	
	insights = {}
	
	lfy['contract_value'] = lfy['contract_value'] #.astype(float)
	cfy['contract_value'] = cfy['contract_value'] #.astype(float)
	insights['sum_contracts_prev_fy'] = functions.format_currency(lfy[lfy['agency.id']==data['agency']['id']]['contract_value'].sum())
	insights['sum_contracts_current_fy'] = functions.format_currency(cfy[cfy['agency.id']==data['agency']['id']]['contract_value'].sum()) #functions.format_currency(
		
	data['contract_value'] = functions.format_currency(data['contract_value'])
	
	# Sum the total earned in the Contracted Agency
	insights['sum_contracts_in_agency_prev_fy'] = humanize.apnumber(lfy['contract_value'][lfy['agency.id'] == data['agency']['id']].sum())
	insights['sum_contracts_in_agency_current_fy'] = humanize.apnumber(cfy['contract_value'][cfy['agency.id'] == data['agency']['id']].sum())
	
	# Find the highest revenue agencies for this and last year
	df_temp = cfy.groupby(['agency.title']).sum().reset_index()
	insights['highest_revenue_current_fy'] = functions.humanise_array(list(df_temp['agency.title'][:4].values))
	
	df_temp = lfy.groupby(['agency.title']).sum().reset_index()
	insights['highest_revenue_prev_fy'] = functions.humanise_array(list(df_temp['agency.title'][:4].values))
	
	# Find all of the open contracts in this agency
	df_temp = contracts[contracts['contract_end']>now_string] # limit to the 'Open' contracts
	df_temp = df_temp[df_temp['agency.id']==contract_data['agency']['id']] # limit it to the current agency
	df_temp = df_temp[df_temp['cn_id']!=contract_data['cn_id']] # exclude the current contract
	insights['contracts_in_agency'] = []
	
	for index, row in df_temp.iterrows():
		temp_dict = {}
		temp_dict['contract_id']=row['id']
		temp_dict['title']=row['title']
		try:
			temp_dict['unspsc'] = row['unspsc.title']
		except:
			temp_dict['unspsc'] = "-"
		temp_dict['contract_value']= "$"+ humanize.intcomma(row['contract_value'])
		contract_end = datetime.strptime(row['contract_end'], '%Y-%m-%d')
		temp_dict['closing_days'] = humanize.naturaltime(contract_end)
		try:
			temp_dict['division_title'] = row['division.title']
			temp_dict['division_id'] = row['division.id']
		except:
			temp_dict['division_title'] = None
			temp_dict['division_id'] = None
		try:
			temp_dict['branch_title'] = row['branch.title']
			temp_dict['branch_id'] = row['branch.id']
		except:
			temp_dict['branch_title'] = None
			temp_dict['branch_id'] = None
		temp_dict['category_temp_title'] = row['category_temp_title']
		insights['contracts_in_agency'].append(temp_dict)
		
	data['insights'] = insights
	
	return render_template('contract.html', data=data)



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
	original_contract_value = data['original_contract_value']
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

	if 'division_id' in data:
		division_id = data['division_id']
	else:
		division_id = None		

	if 'branch_id' in data:
		branch_id = data['branch_id']
	else:
		branch_id = None	

	if 'contact_name' in data:
		contact_name = data['contact_name']
		if contact_name.lower()=="none":
			data['contact_name'] = None
	else:
		contact_name = None	

	contract=Contract.query.filter_by(cn_id=cn_id).first()
	if contract==None:
		db.create_all()
		contract = Contract(original_contract_value=original_contract_value, contact_name=contact_name, branch_id=branch_id, division_id=division_id, title=title, cn_id=cn_id, son_id=son_id, atm_austender_id=atm_id, contract_start=contract_start, contract_end=contract_end, contract_duration=contract_duration, category_temp_title=category_temp_title, agency_id=agency_id, confidentiality_contract=confidentiality_contract, agency_reference_id=agency_reference_id, confidentiality_outputs=confidentiality_outputs, contract_value=contract_value, procurement_method=procurement_method, description=description, publish_date=publish_date, supplier_id=supplier_id)
		db.session.add(contract)
		db.session.commit()
	else:
		# UPDATE ANY CHANGES TO THE OPPORTUNITY
		contract.son_id = son_id
		contract.atm_austender_id = atm_id
		contract.contact_name = contact_name
		contract.branch_id = branch_id
		contract.division_id = division_id
		contract.contract_value = contract_value
		contract.original_contract_value = original_contract_value
		db.session.commit()

	response = ContractSchema().dump(contract).data
	return response




@app.route("/contract/unspsc")
def contract_unspsc():
    # Shows all of the contracts that need to have the UNSPSC linked by the spider.
    try:  
        # reload and only show the ones that need scraping form the unspsc site.
        contract_unspsc = Contract.query.filter_by(unspsc_id = None).all()
        result = ContractSchema(many=True).dump(contract_unspsc).data 

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


# ------------------------------------------- UNSPSC -----------------------------------------
# --------------------------------------------------------------------------------------------


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

        result = UnspscSchema(many=True).dump(unspsc).data  # THIS SHOWS ALL OF THE Ops FOR THE UNSPSCs
        #result = unspscs_simple_schema.dump(unspsc).data
        return json.dumps(result)
        #return jsonify(result)
    except Exception as e:
	    return(str(e))



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

            functions.update_contract_unspsc()
            return functions.json_response('Success - All unspscs Added', None)
        else:
            functions.update_contract_unspsc()
            return functions.json_response('Success - unspsc Already Exists', None)


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
        return functions.json_response('Success - UNSPSC title updated', None)

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
        result = UnspscSchema(many=True).dump(unspsc).data
        result = jsonify(result)
        return result

    except Exception as e:
        return(str(e))



# updates all of the UNSPSCs for each contract
@app.route("/unspsc/update")
def unspsc_update():
    contract_unspsc = Contract.query.filter_by(unspsc_id = None).order_by(desc(Contract.id)).limit(5).all()
    result = ContractSchema(many=True).dump(contract_unspsc).data  

    # Loop through and update from the UNSPSC database
    for item in result:
        #print(item['category_temp_title'])

        obj = Unspsc.query #.all() #session.query(Contract)
        obj = obj.filter(Unspsc.title.ilike(item['category_temp_title']))
        obj = obj.first()

        if obj!=None:
            temp_result = UnspscSchema().dump(obj).data 
            #print(temp_result)
            #print(item['id'])
            
            contract_obj = Contract.query.filter_by(id = item['id']).first()
            contract_obj.unspsc_id = temp_result['id']
            db.session.commit()

    output={"data":"Success"}
    return jsonify(output)

# ------------------------------------------- SON -----------------------------------------
# --------------------------------------------------------------------------------------------


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

        response = SonSchema().dump(son).data
        return functions.json_response('Success - Son Added', response)
    else:
        response = SonSchema().dump(son).data
        return functions.json_response('Success - Son Already Exists', response)



# ------------------------------------------- AGENCY -----------------------------------------
# --------------------------------------------------------------------------------------------

@app.route("/agencies")
def agencies():
    agencies=Agency.query.all()
    result = AgencySchema(many=True).dump(agencies).data
    return render_template('agencies.html', data=result)



@app.route("/agency/<agency_id>", methods=['GET'])
@app.route("/agency/<agency_id>/<division_id>", methods=['GET'])
@app.route("/agency/<agency_id>/<division_id>/<branch_id>", methods=['GET'])
def agency_detail(agency_id, division_id=0, branch_id=0):
	division_id = int(division_id)
	branch_id = int(branch_id)

	data = {} # holds all of the data to be sent to the view
	data['page_data'] = {} #holds the basic display data for the page

	# find the level we want to drill down into the agency results
	drill_down = "agency"
	if division_id>0:
		drill_down = "division"
	if branch_id>0:
		drill_down = "branch"

	agency = Agency.query.filter_by(id=agency_id).first()
	agency_data = AgencySchema().dumps(agency).data
	data['agency_data'] = json.loads(agency_data)
	data['page_data']['subordinate_url'] = "/"+str(data['agency_data']['id'])

	if division_id>0:
		division = Division.query.filter_by(id=division_id).first()
		division_data = DivisionSchema().dumps(division).data
		data['division_data'] = json.loads(division_data)
		data['page_data']['subordinate_url'] = "/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id'])
	else:
		data['division_data'] = None

	if branch_id>0:
		branch = Branch.query.filter_by(id=branch_id).first()
		branch_data = DivisionSchema().dumps(branch).data
		data['branch_data'] = json.loads(branch_data)
		data['page_data']['subordinate_url'] = None

	else:
		data['branch_data'] = None

	# create the dataset for the Agency Page to display the correct level of detail
	data['page_data']['breadcrumbs'] = [{"title":data['agency_data']['title'], "id":data['agency_data']['id'], "link":"/"+str(data['agency_data']['id']) }]
	if drill_down=="agency":
		data['page_data']['title'] = data['agency_data']['title']
		data['page_data']['title_id'] = data['agency_data']['id']
		data['page_data']['subordinates'] = data['agency_data']['divisions']
		data['page_data']['subordinate_name'] = "Divisions"
		data['page_data']['subordinate_name_single'] = "Division"
		data['page_data']['current_name'] = "Agency"
	if drill_down=="division":
		data['page_data']['title'] = data['division_data']['title']
		data['page_data']['title_id'] = data['division_data']['id']
		data['page_data']['subordinates'] = data['division_data']['branches']
		data['page_data']['subordinate_name'] = "Branches"
		data['page_data']['subordinate_name_single'] = "Branch"
		data['page_data']['current_name'] = "Division"
		data['page_data']['breadcrumbs'].append({"title":data['division_data']['title'], "id":data['division_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id']) })
	if drill_down=="branch":
		data['page_data']['title'] = data['branch_data']['title']
		data['page_data']['title_id'] = data['branch_data']['id']
		data['page_data']['subordinates'] = None
		data['page_data']['subordinate_name'] = None
		data['page_data']['subordinate_name_single'] = None
		data['page_data']['current_name'] = "Branch"
		data['page_data']['breadcrumbs'].append({"title":data['division_data']['title'], "id":data['division_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id']) })
		data['page_data']['breadcrumbs'].append({"title":data['branch_data']['title'], "id":data['branch_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id'])+"/"+ str(data['branch_data']['id']) })
		

	# Get all of the contracts for the Agency/Division/Branch
	contracts = Contract.query.filter_by(agency_id=data['agency_data']['id'])
	if division_id>0:
		contracts = contracts.filter( getattr(Contract, "division_id" ) == division_id )
	if branch_id>0:
		contracts = contracts.filter( getattr(Contract, "branch_id" ) == branch_id )
	contracts = contracts.all()
	contract_data = ContractSchema(many=True).dumps(contracts).data
	contract_data = json.loads(contract_data)
	data['contract_data'] = contract_data

	contracts_norm = json_normalize(contract_data) #normalise the JSON for the contracts

	cfy_start, cfy_end, lfy_start, lfy_end, now_string = functions.financial_years() # Only keep the last two financial years
	#contracts_norm = contracts_norm[contracts_norm['contract_start']>=lfy_start]
	#cfy = contracts_norm[contracts_norm['contract_start']>=cfy_start]
	#cfy = cfy[cfy['contract_start']<=cfy_end]
	#lfy = contracts_norm[contracts_norm['contract_start']>=lfy_start]
	#lfy = lfy[lfy['contract_start']<=lfy_end]

	#insights['sum_contracts_prev_fy'] = functions.format_currency(lfy[lfy['agency.id']==data['agency']['id']]['contract_value'].sum())
	#insights['sum_contracts_current_fy'] = functions.format_currency(cfy[cfy['agency.id']==data['agency']['id']]['contract_value'].sum()) #functions.format_currency(
	

	#return data

	return render_template('agency.html', data=data)




@app.route("/agency/add", methods=['GET'])
def agency_add():

    title=request.args.get('title').capitalize()
    try:
        portfolio=request.args.get('portfolio').capitalize()
    except:
        portfolio = None
    
    agency = Agency.query.filter_by(title=title).first()
    if agency==None:
        db.create_all()
        agency = Agency(title=title, portfolio=portfolio)
        db.session.add(agency)
        db.session.commit()

        response = AgencySchema().dump(agency).data
        return functions.json_response('Success - Agency Added', response)
    else:
        agency.portfolio = portfolio
        db.session.commit()

        response = AgencySchema().dump(agency).data
        return functions.json_response('Success - Agency Already Exists', response)


@app.route("/division/add", methods=['GET'])
def division_add():

    title=request.args.get('title').capitalize()
    agency_id=request.args.get('agency_id')
    
    division = Division.query.filter_by(title=title).first()
    if division==None:
        db.create_all()
        division = Division(title=title, agency_id=agency_id)
        db.session.add(division)
        db.session.commit()

        response = DivisionSchema().dump(division).data
        return functions.json_response('Success - division Added', response)
    else:
        response = DivisionSchema().dump(division).data
        return functions.json_response('Success - division Already Exists', response)



@app.route("/branch/add", methods=['GET'])
def branch_add():

    title=request.args.get('title').capitalize()
    division_id=request.args.get('division_id')
    
    branch = Branch.query.filter_by(title=title).first()
    if branch==None:
        db.create_all()
        branch = Branch(title=title, division_id=division_id)
        db.session.add(branch)
        db.session.commit()

        response = BranchSchema().dump(branch).data
        return functions.json_response('Success - branch Added', response)
    else:
        response = BranchSchema().dump(branch).data
        return functions.json_response('Success - branch Already Exists', response)


# ------------------------------------ SUPPLIERS ------------------------------------
# ---------------------------------------------------------------------------------
@app.route("/suppliers")
def suppliers():
	suppliers=Supplier.query.all()
	result = SupplierSchema(many=True).dump(suppliers).data
	return render_template('suppliers.html', data=result, data_json= json.dumps(result))


@app.route("/supplier/<supplier_id>", methods=['GET'])
def supplier_detail(supplier_id):
	supplier = Supplier.query.filter_by(id=supplier_id).first()
	result = SupplierSchema().dumps(supplier).data
	result = json.loads(result)

	data = {}
		
	data['supplier_details'] = result

    # --------------------  ANALYSIS  ------------------------

	#QUERY_ENDPOINT = session['endpoint']+"contracts?paginate=no&supplier_id="+ str(supplier_id)
	#uResponse = requests.get(url = QUERY_ENDPOINT)
	#query_data = json.loads(uResponse.text)

	supplier_contracts = Contract.query.filter_by(supplier_id=supplier_id)
	result = ContractSchema(many=True).dumps(supplier_contracts).data
	result = json.loads(result)

	print(result)	

	#df = result['results']
	df = json_normalize(result)
	if len(df)>0:

		# TEMP FIX ***********************************
		for index, row in df.iterrows():
			try:
				int(row['contract_value'])
			except:
				new_value = row['contract_value'][:row['contract_value'].find("Original:")].strip()
				original_value = row['contract_value'][row['contract_value'].find("Original:")+9:].strip()
				df.at[index,'contract_value'] = new_value
		# TEMP ***********************************

		# FIX THIS TO BE ABLE TO RECOGNISE THE UPDATED CONTRACT VALUEs
		# could not convert string to float: '150040.00                            Original:                121000.00'
		df['contract_value'] = df['contract_value'].astype(float)


		cfy_start, cfy_end, lfy_start, lfy_end, now_string = functions.financial_years()

		cfy = df[df['contract_start']>=cfy_start]
		cfy = cfy[cfy['contract_start']<=cfy_end]
		lfy = df[df['contract_start']>=lfy_start]
		lfy = lfy[lfy['contract_start']<=lfy_end]

		analysis_json ={}
		analysis_json['sum_contracts_prev_fy'] = functions.format_currency(lfy['contract_value'].sum())
		analysis_json['sum_contracts_current_fy'] = functions.format_currency(cfy['contract_value'].sum())

		# Find the highest revenue agencies for this and last year
		df_temp = cfy.groupby(['agency.title']).sum().reset_index()
		analysis_json['highest_revenue_current_fy'] = df_temp['agency.title'][:1].values

		df_temp = lfy.groupby(['agency.title']).sum().reset_index()
		analysis_json['highest_revenue_prev_fy'] = df_temp['agency.title'][:1].values

		# Find all of the open contracts in this agency
		df_temp = df.copy()
		df_temp = df_temp[df_temp['contract_end']>lfy_start]

		analysis_json['open_contracts'] = []
		for index, row in df_temp.iterrows():
			temp_dict = {}
			# is this project ongoing?
			if row['contract_end']>now_string:
				temp_dict['ongoing'] = 1
			else:
				temp_dict['ongoing'] = 0

			if (row['contract_start']>=lfy_start) and (row['contract_start']<=lfy_end):
				temp_dict['year'] = "lfy"
			else:
				temp_dict['year'] = "cfy"

			temp_dict['contract_id']=row['id']
			try:
				temp_dict['division_title']=row['division.title']
			except:
				temp_dict['division_title'] = None

			try:
				temp_dict['branch_title']=row['branch.title']
			except:
				temp_dict['branch_title'] = None

			temp_dict['agency']=row['agency.title']
			try:
				temp_dict['unspsc'] = row['unspsc.title']
			except:
				temp_dict['unspsc'] = ""
			temp_dict['title']=row['title']
			temp_dict['contract_value']= "$"+ humanize.intcomma(row['contract_value'])
			temp_dict['contract_end'] = row['contract_end']
			temp_dict['contract_start'] = row['contract_start']
			contract_end = datetime.strptime(row['contract_end'], '%Y-%m-%d')
			temp_dict['closing_days'] = humanize.naturaltime(contract_end) 
			analysis_json['open_contracts'].append(temp_dict)
        
		data['analysis_json'] = analysis_json

        #  ------------------------  CHARTING  --------------------------

		chart_data = {}
		chart_data['lfy_x'], chart_data['lfy_y'], chart_data['cfy_x'], chart_data['cfy_y'] = charts.chart_revenue(df, lfy_start, lfy_end, cfy_start, cfy_end)
		data['chart_data'] = chart_data

        # Generate the agency revenue chart
		agency_chart_data = {}
		agency_chart_data['agency_list'], agency_chart_data['lfy_values'], agency_chart_data['cfy_values'], agency_chart_data['chart_height'], agency_chart_data['lfy_agencies'], agency_chart_data['cfy_agencies'] = charts.chart_agency_revenue(df, lfy_start, lfy_end, cfy_start, cfy_end)
		data['agency_chart_data'] = agency_chart_data

	else:
		data['analysis_json'] = {}

	return render_template('supplier.html', data=data)




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

        response = SupplierSchema().dump(supplier).data
        return functions.json_response('Success - Supplier Added', response)
    else:
        response = SupplierSchema().dump(supplier).data
        return functions.json_response('Success - Supplier Already Exists', response)




# ------------------------------------ APS EMPLOYEE ------------------------------------
# ---------------------------------------------------------------------------------

@app.route("/staff")
def staff():
	data={}
	aps=Employee.query.limit(2000).all() #.limit(2000)
	aps_staff = EmployeeSchema(many=True).dump(aps).data
	data['aps_staff'] = aps_staff

	for item in data['aps_staff']:
		try:
			item['latest_notice'] = max(item['notices'], key=lambda x:x['notice_no'])
		except:
			item['latest_notice'] = None


	return render_template('aps.html', data=data)


@app.route("/employee/add", methods=['POST'])
def employee_add():

    data = request.form.to_dict()
    print(data)
    first_name = data['employee_first_name']
    last_name = data['employee_last_name']
    employee_no = data['employee_no']
    gender = data['gender']

    employee = Employee.query.filter_by(employee_no=employee_no).first()
    result = EmployeeSchema().dumps(employee).data
    if len(result)>2:
        return functions.json_response('User already exists', result)
    else:
        db.create_all()
        employee = Employee(first_name=first_name, last_name=last_name, employee_no=employee_no, gender=gender)
        db.session.add(employee)
        db.session.commit()

        response = EmployeeSchema().dump(employee).data
        return functions.json_response('Success', response)



# ------------------------------------ APS NOTICE ------------------------------------
# ---------------------------------------------------------------------------------

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
    result = NoticeSchema().dumps(notice).data
    if len(result)>2:
        return functions.json_response('notice already exists', result)
    else:
        db.create_all()
        notice = Notice(publish_date=published, advertised=advertised, position_details=position_details, state=state, suburb=suburb, agency_id=agency_id, notice_no=notice_no, employee_id=employee_id, notice_type=notice_type, classification_from=classification_from, classification=classification, position=position)
        db.session.add(notice)
        db.session.commit()

        response = NoticeSchema().dump(notice).data
        return functions.json_response('Success', response)






# ------------------------------------ RUN APP ------------------------------------
# ---------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
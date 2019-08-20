import os
import requests 
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import and_, or_, not_
from flask_marshmallow import Marshmallow
import json
from datetime import datetime, date, time, timedelta
import humanize
from flask_cors import CORS, cross_origin
import random, string
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import functions, insight_functions # import all of the custom written functions
import charts
from werkzeug.utils import secure_filename


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
ma = Marshmallow(app)
# import all of the database models and schemas
from models import User, UserSchema, Comment, CommentSchema, Op, OpSchema, OpSimpleSchema, Unspsc, UnspscSchema, UnspscSchemaSimple, Agency, AgencySchema, AgencySchemaSimple, Addenda, AddendaSchema, Contract, ContractSchema, Supplier, SupplierSchema, FilterUnspsc, FilterUnspscSchema, Page, Tag, Son, SonSchema, Employee, EmployeeSchema, Notice, NoticeSchema, Division, DivisionSchema, Branch, BranchSchema, ContractCount, ContractCountSchema, SupplierAddress, SupplierAddressSchema, SupplierMatrix, SupplierMatrixSchema, Competitor, CompetitorSchema


# ------------------------------------ TEMP ------------------------------------
# ----------------------------------------------------------------------------------------

import time
@app.route("/update")
def update():

	i=0
	# *** UPDATE THE DISPLAY NAMES
	#query = ContractCount.query.filter_by(id=1).first()
	#query.scrape_date = datetime.now() #10733901  aps_notification
	#db.session.commit()

	time.sleep(1)
	count_ = int(request.args.get('count'))
	if count_=="":
		count_=0

	# update Supplier
	suppliers = Supplier.query.order_by(Supplier.id).filter(Supplier.id>count_).all()
	#query = Supplier.query.filter_by(id>int(count_)).all()
	response = SupplierSchema(many=True).dump(suppliers).data

	for item in response:
		if i>150:
			break
		query = Supplier.query.filter_by(id=item['id']).first()
		query.name = item['name'].lower()
		db.session.commit()
		i=i+1
		count_=count_+1

	link = "<a href='/update?count="+ str(count_) +"'>Next</a>"
	link = "<script>window.location.href = '/update?count="+ str(count_) +"';</script>"

	return str(link)
	return redirect(url_for('update_display_name')+"?count="+str(count_))

	# update agencies
	#agency = Agency.query.filter_by(display_title=None).all()
	#response = AgencySchema(many=True).dump(agency).data

	#for item in response:
	#	if i>500:
	#		break
	#	display_title = functions.cleanTitle(item['title'].title())
	#	query = Agency.query.filter_by(id=item['id']).first()
	#	query.display_title = display_title
	#	db.session.commit()
	#	i = i + 1


	# update Divisions
	#division = Division.query.filter_by(display_title=None).all()
	#response = DivisionSchema(many=True).dump(division).data

	#for item in response:
	#	if i>500:
	#		break
	#	display_title = functions.cleanTitle(item['title'].title())
	#	query = Division.query.filter_by(id=item['id']).first()
	#	query.display_title = display_title
	#	db.session.commit()
	#	i = i + 1


	# update Branches
	#branch = Branch.query.filter_by(display_title=None).all()
	#response = BranchSchema(many=True).dump(branch).data

	#for item in response:
	#	if i>500:
	#		break
	#	display_title = functions.cleanTitle(item['title'].title())
	#	query = Branch.query.filter_by(id=item['id']).first()
	#	query.display_title = display_title
	#	db.session.commit()
	#	i = i + 1


	# update Supplier
	#supplier = Supplier.query.filter_by(display_name=None).all()
	#response = SupplierSchema(many=True).dump(supplier).data

	#for item in response:
	#	if i>500:
	#		break
	#	display_title = functions.cleanTitle(item['name'].title())
	#	query = Supplier.query.filter_by(id=item['id']).first()
	#	query.display_name = display_title
	#	db.session.commit()
	#	i = i + 1


	#return str("Done")

def all_agencies_segments():
	# Get UNSPSC Segments
	query = Unspsc.query.filter_by(level_int=1).all()
	data = UnspscSchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	#unspsc_segments = []
	#unspsc_dict = {}
	#for item in data:
	#	unspsc_segments.append(item['id'])
	#	unspsc_dict[item['unspsc'][:2]]=int(item['id'])

	unspsc_segments = []
	unspsc_dict = {}
	for item in data:
		unspsc_segments.append(item['id'])
		unspsc_dict[item['unspsc'][:2]]=int(item['id'])
		#unspsc_dict[item['unspsc'][:4]]=int(item['id'])

	query = Unspsc.query.filter_by(level_int=2).all()
	data = UnspscSchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	unspsc_families = []
	for item in data:
		unspsc_segments.append(item['id'])
		unspsc_dict[item['unspsc'][:4]]=int(item['id'])


	# Get all agenceis 
	query = Agency.query.all()
	data = AgencySchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	agencies = []
	for item in data:
		agencies.append(item['id'])

	return unspsc_segments, agencies


@app.route("/competitor_data", methods=['GET'])
def competitor_data():
	supplier_id=int(request.args.get('supplier_id'))
	
	query = Competitor.query.order_by(desc(Competitor.score)).filter_by(supplier_id=supplier_id).all()
	result = CompetitorSchema(many=True).dump(query).data
	data = {"data": result}
	
	return jsonify(data)


@app.route("/comp_matrix/<target_supplier>/<count>", methods=['GET'])
def comp_matrix(target_supplier, count):

	year=int(request.args.get('year'))

	# If it is the first time through. Delete all of the entries for this supplier, so they can be replaced.
	if int(count)==0:
		query = Competitor.query.filter_by(supplier_id=target_supplier).delete()
		db.session.commit()

	#try:
	# Get Matrix for the target supplier
	query = SupplierMatrix.query.filter_by(supplier_id=target_supplier).filter_by(matrix_type="agency_segment").filter_by(financial_year=int(year)).first() 
	data = SupplierMatrixSchema().dumps(query).data

	data = json.loads(data)
	if len(data)>0:

		json_dict = json.loads(data['json']['data'])
		matrix_a_unspsc = []
		matrix_a_agencies = []
		
		for agency in json_dict:
			matrix_a_agencies.append(agency)
			for unspsc in json_dict[agency]:
				matrix_a_unspsc.append(str(unspsc))

		matrix_a_json_data = data['json']['data']

		#json_data = data['json']['data']
		# find all of the agencies and segments so the matrix can be rebuilt
		#unspscs, agencies = all_agencies_segments()
		#print(agencies)
		# Rebuild the matrix
		#matrix_a = insight_functions.rebuild_matrix(json_data, unspscs, agencies)

		#Limit this to compare n competitors
		query = SupplierMatrix.query.filter(SupplierMatrix.matrix_type=="agency_segment").filter(SupplierMatrix.supplier_id>=int(count)).order_by(SupplierMatrix.supplier_id).limit(10).all()
		data = SupplierMatrixSchema(many=True).dumps(query).data
		# if there are no more suppliers to compare
		if len(data)==2:
			return "Done"
		supplier_matrices = json.loads(data)

		# Arrays to create a dataframe when this batch is complete
		supplier_id = []
		comp_score = []

		for supplier in supplier_matrices:
			# Get Matrices
			#try:

			if len(supplier['json']['data'])>3:

				json_dict = json.loads(supplier['json']['data'])

				unspscs = []
				agencies = []
				
				for item in matrix_a_unspsc:
					unspscs.append(item)
				for item in matrix_a_agencies:
					agencies.append(item)
				
				for agency in json_dict:
					agencies.append(agency)
					for unspsc in json_dict[agency]:
						unspscs.append(str(unspsc))

				#json_data = supplier['json']['data']

				matrix_a = insight_functions.rebuild_matrix(matrix_a_json_data, unspscs, agencies)

				matrix_b_json_data = supplier['json']['data']
				matrix_b = insight_functions.rebuild_matrix(matrix_b_json_data, unspscs, agencies)

				supplier_id.append(supplier['supplier']['id'])

				comp_score.append( insight_functions.calc_competition(matrix_a, matrix_b) )
			#except:
			#	print("something broke on line 209 of app.py")
			#break

		# Create the scores dataframe, sort and filter by competitor score
		comp_scores = pd.DataFrame()
		comp_scores['supplier_id'] = supplier_id
		comp_scores['score'] = comp_score
		comp_scores.set_index('supplier_id', drop=True, append=False, inplace=True, verify_integrity=False)
		comp_scores = comp_scores.sort_values(by='score', ascending=0)
		print("SCORE")
		print(comp_scores)
		
		comp_scores = comp_scores[comp_scores['score']>-1]
		comp_scores = comp_scores[comp_scores['score']!=0]
		#comp_scores = comp_scores[:50]# only save the top 50 competitors for each

		


		#db.create_all()
		for index, row in comp_scores.iterrows():
			#print(index, row['score'])
			if index>(int(count)+100):
				count=int(index)
			# Check the record does not exist
			query = Competitor.query.filter_by(supplier_id=target_supplier).filter_by(competitor_id=index).first() 
			if query==None:
				# Add the record to the competitor table
				query = Competitor(supplier_id=target_supplier, competitor_id=index, score=row['score'], created=datetime.now())
				db.session.add(query)
				db.session.commit()

		#except:
		#	pass

		#return "Done"
	
	#return redirect("/comp_matrix/"+ str(target_supplier) +"/"+str(int(count)+100))

	link = "<script>window.location.href = '/comp_matrix/"+ str(target_supplier) +"/"+str(int(count)+10)+"?year="+ str(year) +"';</script>"
	#link = "<a href='/comp_matrix/"+ str(int(target_supplier)+1) +"'>Next</a>"
	#link = "<script>window.location.href = '/comp_matrix/"+ str(int(target_supplier)+1) +"';</script>"
	return str(link)


@app.route("/matrix/<target_supplier>", methods=['GET'])
def matrix(target_supplier):

	try:
		loop=int(request.args.get('loop'))
	except:
		loop=0

	year=int(request.args.get('year'))

	if int(target_supplier)==0:
		query = SupplierMatrix.query.delete() #.filter_by(supplier_id=target_supplier)
		db.session.commit()

	# Creates the matrix for the supplier for a year/financial quarter.
	# Automagically loops through from the supplier_id provided, until it gets to the end.
	
	# Get UNSPSC Segments
	#query = Unspsc.query.filter(Unspsc.level_int.in_([1])).all()
	query = Unspsc.query.filter_by(level_int=1).all()
	data = UnspscSchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	unspsc_segments = []
	unspsc_dict = {}
	for item in data:
		unspsc_segments.append(item['id'])
		unspsc_dict[item['unspsc'][:2]]=int(item['id'])
		#unspsc_dict[item['unspsc'][:4]]=int(item['id'])

	query = Unspsc.query.filter_by(level_int=2).all()
	data = UnspscSchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	unspsc_families = []
	for item in data:
		unspsc_families.append(item['id'])
		unspsc_dict[item['unspsc'][:4]]=int(item['id'])


	# Get all agenceis 
	query = Agency.query.all()
	data = AgencySchemaSimple(many=True).dumps(query).data
	data = json.loads(data)

	agencies = []
	for item in data:
		agencies.append(item['id'])


	search_suppliers = [int(target_supplier)]

	# Find all of the children if it is an umbrella
	query = Supplier.query.filter_by(umbrella_id=int(target_supplier)).all()
	data = SupplierSchema(many=True).dumps(query).data
	data = json.loads(data)
	for item in data:
		# Add the IDs of the children to the search
		if item['id'] not in search_suppliers:
			search_suppliers.append(item['id'])

	
	# NEED TO ADD IN A DATE FILTER HERE !!!!!!  SO WE ARE NOT PROCESSING SUCH MASSIVE DATA SETS
	query = Contract.query.filter(Contract.supplier_id.in_(search_suppliers)).all()
	data = ContractSchema(many=True).dumps(query).data
	data = json.loads(data)

	#print(data)

	if len(data)>0:
		df = insight_functions.clean_contract_df(data)

		financial_year = year
		financial_quarter = 0

		# Loop over suppliers and add the matrix to the db
		#for supplier_id in supplier_ids:
		matrixes = insight_functions.supplier_agency_segment_matrix(df, target_supplier, unspsc_segments, unspsc_dict, agencies, financial_year, financial_quarter)

		if matrixes!=None:
			for matrix in matrixes:
				if len(matrix['data'])>2:
					# Add the matrix to the db
					obj=SupplierMatrix.query.filter_by(supplier_id=matrix['supplier_id']).filter_by(financial_year=financial_year).filter_by(financial_quarter=financial_quarter).first()
					if obj==None:
						db.create_all()
						query = SupplierMatrix(matrix_type="agency_segment", supplier_id=target_supplier, json=matrix, financial_year=financial_year, financial_quarter=financial_quarter, created=datetime.now())
						db.session.add(query)
						db.session.commit()
					else:
						response = OpSchema().dump(obj).data # get the existing op data
						# Update any changes to the opportunity
						obj.json = matrix
						created=datetime.now()
						db.session.commit()

	if loop==1:
		link = "<a href='/matrix/"+ str(int(target_supplier)+1) +"?loop="+ str(loop) +"'>Next</a>"
		link = "<script>window.location.href = '/matrix/"+ str(int(target_supplier)+1) +"?loop="+ str(loop) +"&year="+ str(year) +"';</script>"
		return str(link)
	else:
		return "Done"


	#data = {"result": True}
	#return jsonify(data)


# ------------------------------------ LOGIN / LOGOUT ------------------------------------
# ----------------------------------------------------------------------------------------


# --- LANDING PAGE ---
@app.route("/")
def landing():
    return render_template('index.html')


# --- DASHBOARD PAGE ---
@app.route("/dashboard")
def dashboard():
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
			session['last_name'] = result['last_name']
			session['user_id'] = result['id']
			session['user_token'] = result['token']
			session['admin'] = result['admin']

			return redirect(url_for('op'))
		else:
			return redirect(url_for('login')+"?error=1")

	return render_template('login.html', form=form, data=data)


# --- LOGOUT PAGE ---
@app.route("/logout")
def logout():
	session['first_name'] = None
	session['last_name'] = None
	session['user_id'] = None
	session['user_token'] = None
	session['admin'] = None
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
		hide_op = False
		published = datetime.strptime(op['publish_date'], '%Y-%m-%d')
		op['published_date_human'] = humanize.naturalday(published)
		close_date = datetime.now() - datetime.strptime(op['close_date'], '%Y-%m-%d')
		op['close_date_human'] = humanize.naturaltime(close_date)
		op['title'] = op['title'].capitalize()
		op['category_display'] = max(op['categories'], key=lambda x:x['level_int']) # Get the highest (most specific) category provided for the ATM
		
		for category in op['categories']:
			if category['id'] in unspsc_filters:
				hide_op = True

		if hide_op==False:
			output['results'].append(op)
		
        
	return render_template('opportunities.html', data=output)




@app.route("/op/<op_id>", methods=['GET'])
def op_detail(op_id):
	#try:
	opportunity = Op.query.filter_by(id=op_id).first()
	result = OpSchema().dumps(opportunity).data
	result = json.loads(result)

	published = datetime.now() - datetime.strptime(result['publish_date'], '%Y-%m-%d')
	result['published_date_human'] = humanize.naturaltime(published)
	close_date = datetime.now() - datetime.strptime(result['close_date'], '%Y-%m-%d')
	result['close_date_human'] = humanize.naturaltime(close_date)

	result['description'] = result['description'].strip()
	result['description'] = result['description'].replace("\r\n", "")
	result['description'] = result['description'].replace("<p>\xa0</p>", "")

	
	# Loop through and add the categories to segment/class etc.
	#result['category_display'] = max(result['categories'], key=lambda x:x['level_int']) # Get the highest (most specific) category provided for the ATM
	result['unspsc_segment'] = None
	result['unspsc_family'] = None
	result['unspsc_class'] = None
	result['unspsc_commodity'] = None

	category_dict = []  #[ {"level":"family",  "data":result['unspsc_family']}, {"level":"class",  "data":result['unspsc_class']}, {"level":"commodity",  "data":result['unspsc_commodity']}]
	category_list = []  #[result['unspsc_family']['id'], result['unspsc_class']['id'], result['unspsc_commodity']['id']]

	for category in result['categories']:
		if category['level_int']==1:
			result['unspsc_segment'] = category
		elif category['level_int']==2:
			result['unspsc_family'] = category

			# add all of the suboordinate classes
			temp_ids = []
			query = Unspsc.query.filter(Unspsc.parent_id==result['unspsc_family']['id']).all() #result['unspsc_family']['id']
			data_temp = UnspscSchema(many=True).dumps(query).data
			data_temp = json.loads(data_temp)
			for item in data_temp:
				temp_ids.append(item['id'])

			# add all of the suboordinate commodities
			query = Unspsc.query.filter(Unspsc.parent_id.in_(temp_ids)).all()
			data_temp = UnspscSchema(many=True).dumps(query).data
			data_temp = json.loads(data_temp)	
			for item in data_temp:
				temp_ids.append(item['id'])

			temp_ids.append(result['unspsc_family']['id'])
			print("Family IDS:")
			print(temp_ids)
			category_dict.append( {"level":"family",  "data":result['unspsc_family'], "ids": temp_ids } )

			category_list.append( result['unspsc_family']['id'] )

		elif category['level_int']==3: # FIX THIS!!!!!
			result['unspsc_class'] = category

			# add all of the suboordinate commodities
			temp_ids = []
			query = Unspsc.query.filter(Unspsc.parent_id==result['unspsc_class']['id']).all() #result['unspsc_family']['id']
			data_temp = UnspscSchema(many=True).dumps(query).data
			data_temp = json.loads(data_temp)
			for item in data_temp:
				temp_ids.append(item['id'])

			temp_ids.append(result['unspsc_class']['id'])
			print("Class IDS:")
			print(temp_ids)
			category_dict.append( {"level":"class",  "data":result['unspsc_class'], "ids": temp_ids } )
			category_list.append( result['unspsc_class']['id'] )
		elif category['level_int']==4: # FIX THIS!!!!!
			result['unspsc_commodity'] = category

			temp_ids = []
			temp_ids.append(result['unspsc_commodity']['id'])
			print("Commodity IDS:")
			print(temp_ids)
			category_dict.append( {"level":"commodity",  "data":result['unspsc_commodity'], "ids": temp_ids } )
			category_list.append( result['unspsc_commodity']['id'] )

	
	result['panel_arrangement'] = 'Yes' if result['panel_arrangement'] == 1 else 'No'
	result['multi_stage'] = 'Yes' if result['multi_stage'] == 1 else 'No'
	result['multi_agency_access'] = 'Yes' if result['multi_agency_access'] == 1 else 'No'
	

	# Query all contracts from the database

	#the_value = 141
	#db.session.query(Contract).filter(Contract.categories.contains(
    #{'categrories': [{'id': the_value}]}
	#))
	#https://stackoverflow.com/questions/39460387/sqlalchemy-filtering-on-values-stored-in-nested-list-of-the-jsonb-field



	query = Contract.query.filter(Contract.unspsc_id.in_(category_list)).all()
	data = ContractSchema(many=True).dumps(query).data
	data = json.loads(data)
	#print(data)

	contract_data = insight_functions.opportunity(data, result['agency']['id'], category_dict)

	return render_template('opportunity.html', data=result, contract_data=contract_data)

	#except Exception as e:
	#	return(str(e))



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


@app.route("/contracts_data", methods=['GET'])
def contracts_data():
	page=int(request.args.get('page'))
	
	if page==0: # only return the number of pages in the dataset
		query = Contract.query.order_by(desc(Contract.publish_date)).paginate(1, 1, False)
		data = {"data": {}, "pages": query.pages}
	else: # return the dataset
		query = Contract.query.paginate(page, 200, False)
		items=query.items
		result = ContractSchema(many=True).dump(items).data
		data = {"data": result, "pages": query.pages}
	return jsonify(data)



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


# returns the latest contract, for the contract scraping bot
@app.route("/latest_contract")
def latest_contract():
	query = ContractCount.query.first()
	result = ContractCountSchema().dump(query).data
	data = {"scrape_date": result['scrape_date']}
	return jsonify(data)


@app.route("/latest_contract_update", methods=['GET', 'POST'])
def latest_contract_update():

	latest_scrape = request.args.get('latest_scrape')
	latest_scrape = datetime.strptime(latest_scrape, '%Y-%m-%d')
	query = ContractCount.query.first()
	if query==None:
		db.create_all()
		query = ContractCount(scrape_date=datetime.now())
		db.session.add(query)
		db.session.commit()

	query.scrape_date = latest_scrape
	db.session.commit()
	data = {"result": True }
	return jsonify(data)



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
	try:
		publish_date = data['publish_date']
	except:
		publish_date = contract_start
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
		contract.supplier_id = supplier_id
		contract.son_id = son_id
		contract.atm_austender_id = atm_id
		contract.contact_name = contact_name
		contract.branch_id = branch_id
		contract.division_id = division_id
		contract.contract_value = contract_value
		contract.original_contract_value = original_contract_value
		db.session.commit()

	response = ContractSchema().dump(contract).data

	# UNCOMMENT THIS ONCE ALL THE CONTRACT BACKLOG HAS BEEN SCRAPED, AND WE ARE OPERATNG ON A DAILY UPDATE SCHEDULE
	# update the matrix for the supplier
	#matrix(supplier_id)

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
    contract_unspsc = Contract.query.filter_by(unspsc_id = None).order_by(desc(Contract.id)).limit(500).all()
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
	data['page_data']['breadcrumbs'] = [{"title":data['agency_data']['display_title'], "id":data['agency_data']['id'], "link":"/"+str(data['agency_data']['id']) }]
	if drill_down=="agency":
		data['page_data']['title'] = data['agency_data']['display_title']
		data['page_data']['title_id'] = data['agency_data']['id']
		data['page_data']['subordinates'] = data['agency_data']['divisions']
		data['page_data']['subordinate_name'] = "Divisions"
		data['page_data']['subordinate_name_single'] = "Division"
		data['page_data']['current_name'] = "Agency"
	if drill_down=="division":
		data['page_data']['title'] = data['division_data']['display_title']
		data['page_data']['title_id'] = data['division_data']['id']
		data['page_data']['subordinates'] = data['division_data']['branches']
		data['page_data']['subordinate_name'] = "Branches"
		data['page_data']['subordinate_name_single'] = "Branch"
		data['page_data']['current_name'] = "Division"
		data['page_data']['breadcrumbs'].append({"title":data['division_data']['display_title'], "id":data['division_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id']) })
	if drill_down=="branch":
		data['page_data']['title'] = data['branch_data']['display_title']
		data['page_data']['title_id'] = data['branch_data']['id']
		data['page_data']['subordinates'] = None
		data['page_data']['subordinate_name'] = None
		data['page_data']['subordinate_name_single'] = None
		data['page_data']['current_name'] = "Branch"
		data['page_data']['breadcrumbs'].append({"title":data['division_data']['display_title'], "id":data['division_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id']) })
		data['page_data']['breadcrumbs'].append({"title":data['branch_data']['display_title'], "id":data['branch_data']['id'], "link":"/"+str(data['agency_data']['id'])+"/"+ str(data['division_data']['id'])+"/"+ str(data['branch_data']['id']) })
		

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
        agency = Agency(title=title, portfolio=portfolio, display_title=functions.cleanTitle(title))
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
        division = Division(title=title, agency_id=agency_id, display_title=functions.cleanTitle(title))
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
        branch = Branch(title=title, division_id=division_id, display_title=functions.cleanTitle(title))
        db.session.add(branch)
        db.session.commit()

        response = BranchSchema().dump(branch).data
        return functions.json_response('Success - branch Added', response)
    else:
        response = BranchSchema().dump(branch).data
        return functions.json_response('Success - branch Already Exists', response)


# ------------------------------------ SUPPLIERS ------------------------------------
# ---------------------------------------------------------------------------------

@app.route("/temp")
def temp():
	suppliers=Supplier.query.all()
	result = SupplierSchema(many=True).dump(suppliers).data
	return jsonify(result)


@app.route("/suppliers")
def suppliers():
	#suppliers=Supplier.query.all()
	#result = SupplierSchema(many=True).dump(suppliers).data
	#, data=result, data_json= json.dumps(result)
	return render_template('suppliers.html')

@app.route("/suppliers_data", methods=['GET', 'POST'])
def suppliers_data():
	page=int(request.args.get('page'))
	query = Supplier.query.paginate(page, 200, False)
	suppliers=query.items
	
	result = SupplierSchema(many=True).dump(suppliers).data
	for item in result:
		item['link']="<a href='/supplier/"+ str(item['id']) +"'>"+ item['display_name'] +"</a>"
	data = {"data": result, "pages": query.pages}

	return jsonify(data)


@app.route("/supplier/<supplier_id>", methods=['GET'])
def supplier_detail(supplier_id):
	# Get all of the details for the supplier
	supplier = Supplier.query.filter_by(id=supplier_id).first()
	result = SupplierSchema().dumps(supplier).data
	result = json.loads(result)

	data = {}
		
	data['supplier_details'] = result

	# Get all of the suppiers competitors
	query = Competitor.query.order_by(desc(Competitor.score)).filter_by(supplier_id=supplier_id).all()
	result = CompetitorSchema(many=True).dump(query).data
	data['competitors'] = result

	# If the supplier has an parent umbrella supplier, find all the details for the parent
	if data['supplier_details']['umbrella_id']!=None:
		query = Supplier.query.filter_by(id=data['supplier_details']['umbrella_id']).first()
		result = SupplierSchema().dumps(query).data
		result = json.loads(result)
		data['supplier_details']['umbrella_name'] = result['display_name']
	
	# If the supplier is an umbrella supplier, find all of the children
	if data['supplier_details']['umbrella']==1:
		children_suppliers_list = []
		query = Supplier.query.filter_by(umbrella_id=supplier_id).all()
		result = SupplierSchema(many=True).dumps(query).data
		result = json.loads(result)
		data['children_suppliers'] = result
		for item in data['children_suppliers']:
			children_suppliers_list.append(item['id'])
	else:
		data['children_suppliers'] = None

    # --------------------  ANALYSIS  ------------------------

	#QUERY_ENDPOINT = session['endpoint']+"contracts?paginate=no&supplier_id="+ str(supplier_id)
	#uResponse = requests.get(url = QUERY_ENDPOINT)
	#query_data = json.loads(uResponse.text)

	# If the supplier is an umbrella supplier, find the results for all of the children
	if data['supplier_details']['umbrella']==1:
		supplier_contracts = Contract.query.filter(Contract.supplier_id.in_((children_suppliers_list))).all()
	else:
		supplier_contracts = Contract.query.filter_by(supplier_id=supplier_id)
	result = ContractSchema(many=True).dumps(supplier_contracts).data
	result = json.loads(result)

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
			elif (row['contract_start']>=cfy_start) and (row['contract_start']<=cfy_end):
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


# ------------------------------------ SUPPLIER ADDRESS ------------------------------------
# ---------------------------------------------------------------------------------


@app.route("/address/add", methods=['GET'])
def address_add():

	postal_address=request.args.get('postal_address')
	town_city=request.args.get('town_city')
	postcode=request.args.get('postcode')
	country=request.args.get('country')
	supplier_id=request.args.get('supplier_id')
	correct_at=request.args.get('correct_at')

	address = SupplierAddress.query.filter_by(supplier_id=supplier_id).filter_by(postal_address=postal_address).first()
	if address==None:
		db.create_all()
		query = SupplierAddress(postal_address=postal_address, town_city=town_city, postcode=postcode, country=country, supplier_id=supplier_id, correct_at=correct_at)
		db.session.add(query)
		db.session.commit()

		response = SupplierAddressSchema().dump(query).data
		return functions.json_response('Success - Address Added', response)
	else:
		response = SupplierAddressSchema().dump(address).data
		return functions.json_response('Success - Address Already Exists', response)

	




@app.route("/suppliers/add", methods=['GET'])
def suppliers_add():

	name=request.args.get('name').lower()
	abn=request.args.get('abn')
	country=request.args.get('country')
	try:
		country = country.capitalize()
	except:
		pass

    
	if abn.lower()!="exempt":
		print("entered - has an abn")
		supplier = Supplier.query.filter_by(abn=abn).first()
	else:
		print("entered - exempt, checking by name")
		supplier = Supplier.query.filter_by(name=name).first()

	if supplier==None:
		db.create_all()
		supplier = Supplier(name=name, abn=abn, country=country, display_name=functions.cleanTitle(name))
		db.session.add(supplier)
		db.session.commit()

		response = SupplierSchema().dump(supplier).data
		return functions.json_response('Success - Supplier Added', response)
	else:
		supplier.name = name
		db.session.commit()

		response = SupplierSchema().dump(supplier).data
		return functions.json_response('Success - Supplier Already Exists', response)




# ------------------------------------ APS EMPLOYEE ------------------------------------
# ---------------------------------------------------------------------------------

@app.route("/staff")
def staff():
	return render_template('aps.html')


# returns the latest contract, for the contract scraping bot
@app.route("/latest_notice")
def latest_notice():
	query = ContractCount.query.first()
	result = ContractCountSchema().dump(query).data
	data = {"aps_notification": result['aps_notification']}
	return jsonify(data)


@app.route("/latest_notice_update", methods=['GET', 'POST'])
def latest_notice_update():
	latest_notice=int(request.args.get('latest_notice'))
	query = ContractCount.query.filter_by(id=1).first()
	query.aps_notification = latest_notice
	db.session.commit()	


@app.route("/staff_data", methods=['GET', 'POST'])
def staff_data():
	page=int(request.args.get('page'))
	query = Employee.query.paginate(page, 200, False)
	aps_staff=query.items
	result = EmployeeSchema(many=True).dump(aps_staff).data
	for item in result:
		# fetch the latest notice available for the employee
		try:
			item['latest_notice'] = max(item['notices'], key=lambda x:x['notice_no'])
			item['classification'] = item['latest_notice']['classification']
			item['agency'] = item['latest_notice']['agency']['title']
			item['position_details'] = item['latest_notice']['position_details']
			item['publish_date'] = item['latest_notice']['publish_date']
		except: 
			item['latest_notice'] = None
			item['classification'] = None
			item['agency'] = None
			item['position_details'] = None
			item['publish_date'] = None

		item['link']="<a href='/staff/"+ str(item['id']) +"'>"+ item['employee_no'] +"</a>"
	data = {"data": result, "pages": query.pages}
	return jsonify(data)


@app.route("/staff/<staff_id>")
def staff_detail(staff_id):
	query=Employee.query.filter_by(id=staff_id).first()
	result = EmployeeSchema().dump(query).data
	# Find the latest of the contract notices
	try:
		result['latest_notice'] = max(result['notices'], key=lambda x:x['notice_no'])
		result['classification'] = result['latest_notice']['classification']
		result['agency'] = result['latest_notice']['agency']['title']
		result['position_details'] = result['latest_notice']['position_details']
		result['publish_date'] = result['latest_notice']['publish_date']
	except:
		result['latest_notice'] = None
		result['classification'] = None
		result['agency'] = None
		result['position_details'] = None
		result['publish_date'] = None

	data = {"employee_data": result}
	return render_template('staff_member.html', data=data)



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




# ------------------------------------ FILTERS ------------------------------------
# ---------------------------------------------------------------------------------



@app.route("/filter/unspsc/add", methods=['GET'])
def filter_unspsc_add():

	unspsc_id=request.args.get('unspsc_id')

    # Check the token matches the user ID, if not return empty results.
    #user_id = request.args.get('id')
    #token = request.args.get('token')
    #user = User.query.filter_by(id=user_id).filter_by(token=token).first()
    #result = UserSchema().dumps(user).data
    #if len(result)<=2:
    #    output = {"results": []}
    #    return jsonify(output)  
    #else:
	db.create_all()
	filter_ = FilterUnspsc(user_id=session['user_id'], unspsc_id=unspsc_id)
	db.session.add(filter_)
	db.session.commit()

	response = FilterUnspscSchema().dump(filter_).data

	return redirect(url_for('op'))
	#return functions.json_response('Success - Added Filter', response)





# ------------------------------------ ADMIN ------------------------------------
# ---------------------------------------------------------------------------------

# --- DASHBOARD PAGE ---
@app.route("/admin")
def admin():
    return render_template('admin.html')



from forms import SupplierAdmin

@app.route("/admin/supplier/<supplier_id>", methods=['GET', 'POST'])
def admin_supplier(supplier_id):
	# --- This Admin page edits an existing Supplier ---
	form = SupplierAdmin()
	query=Supplier.query.filter_by(id=supplier_id).first()
	result = SupplierSchema().dump(query).data

	if form.validate_on_submit():
		f = form.image.data
		if f!=None:
			filename = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)) + secure_filename(f.filename)
			f.save(os.path.join(
				'static/uploads', filename
			))
			# update the Supplier image path record
			query = Supplier.query.filter_by(id=supplier_id).first()
			if query!=None:
				query.image_url = filename
				db.session.commit()
		
		# update the Details image path record
		query = Supplier.query.filter_by(id=supplier_id).first()
		if query!=None:
			query.display_name = form.display_name.data
			if form.umbrella_id.data!="":
				query.umbrella_id = form.umbrella_id.data
			db.session.commit()

		return redirect('/supplier/'+supplier_id)

	form.display_name.default = result['display_name']
	form.umbrella_id.default = result['umbrella_id']
	form.process()

	return render_template('admin_supplier.html', data=result, form=form)



from forms import CreateUmbrellaSupplier
@app.route("/admin/umbrella_supplier", methods=['GET', 'POST'])
def admin_umbrella_supplier():
	# --- This Admin page creates an umbrella Supplier ---
	form = CreateUmbrellaSupplier()

	if form.validate_on_submit():
		# Add the Umbrella Supplier
		db.create_all()
		supplier_name = Supplier(name=form.supplier_name.data, display_name=form.supplier_name.data, abn='Multiple', country="N/A", umbrella=1)
		db.session.add(supplier_name)
		db.session.commit()

		return redirect(url_for('admin'))

	return render_template('admin_umbrella_supplier.html', form=form)




# ------------------------------------ RUN APP ------------------------------------
# ---------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
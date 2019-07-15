import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_marshmallow import Marshmallow
import json
from datetime import datetime, date, time
from datetime import timedelta
import humanize

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
print(db)
from models import User, UserSchema, Comment, CommentSchema, Op, OpSchema, Unspsc, UnspscSchema, UnspscSchemaSimple, Agency, AgencySchema, Addenda, AddendaSchema, Contract, ContractSchema, Page, Tag


# ---------------- LOAD SCHEMAS ---------------

user_schema = UserSchema()
users_schema = UserSchema(many=True)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

op_schema = OpSchema()
ops_schema = OpSchema(many=True)

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


# ---------------- ROUTES ---------------

@app.route("/")
def hello():


    #db.session.query(Op).delete()
    #db.session.commit()

    #opportunity = Op.query.filter_by(id=240).first()
    opportunity = Op.query.first()
    opportunity.categories = []
    #opportunity.categories.remove(somecategory)
    db.session.commit()
    db.session.delete(opportunity)
    db.session.commit()

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


@app.route("/user/add", methods=['GET'])
def user_add():

    first_name=request.args.get('first_name')
    last_name=request.args.get('last_name')
    email=request.args.get('email')
    
    db.create_all()
    user = User(first_name=first_name, last_name=last_name, email=email)
    db.session.add(user)
    db.session.commit()

    response = user_schema.dump(user).data
    return api_response('Success - Added User', response)



@app.route("/users/delete/<id_>")
def users_delete(id_):
    try:
        obj=User.query.filter_by(id=id_).one()
        db.session.delete(obj)
        db.session.commit()
        return "User deleted. user id={}".format(id_)
    except Exception as e:
	    return(str(e))





# ------------  OPPORTUNITIES ---------------

@app.route("/op")
def op():
    try:
        opportunities=Op.query.order_by(desc(Op.publish_date)).all()
        result = ops_schema.dump(opportunities).data
        
        output = {}
        # Update all of the times to human readable
        for op in result:
            published = datetime.now() - datetime.strptime(op['publish_date'], '%Y-%m-%d')
            op['published_date_human'] = humanize.naturaltime(published)
            close_date = datetime.now() - datetime.strptime(op['close_date'], '%Y-%m-%d')
            op['close_date_human'] = humanize.naturaltime(close_date)

        output['result'] = result

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
        #estimated_value = db.Column(db.String()) #estimated_value_(aud)
        #location = db.Column(db.String()) ## NEEDS WORK act, nsw, vic, sa, wa, qld, nt, tas"
        #addenda_available = data['addenda_available']  #NEEDS WORK
        
        

        obj=Op.query.filter_by(atm_id=atm_id).first()
        if obj==None:
            #db.session.add(opportunity)
            #data = opportunity
            #db.session.add(comment)

            db.create_all()
            opportunity = Op(title=title, atm_id=atm_id, description=description, atm_type=atm_type, publish_date=publish_date, close_date=close_date, agency_id=agency_id, conditions_for_participation=conditions_for_participation, panel_arrangement=panel_arrangement, timeframe_for_delivery=timeframe_for_delivery, multi_stage=multi_stage, multi_agency_access=multi_agency_access, address_for_lodgement=address_for_lodgement)
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
            # UPDATE ANY CHANGES TO THE AOPPORTUNITY
            #db.session.query(Op).filter(id == obj.id).\
            #    update({op.title:title, op.atm_id:atm_id, op.description:description, op.atm_type:atm_type, op.publish_date:publish_date, op.close_date:close_date, op.agency_id:agency_id}, synchronize_session=False)
            #db.session.commit()
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


@app.route("/contract")
def contract():
    try:
        #contracts=Contract.query.order_by(desc(Contract.publish_date)).all()
        contracts=Contract.query.all()
        result = contracts_schema.dump(contracts).data
        return jsonify(result)

    except Exception as e:
	    return(str(e))


@app.route("/contract/add", methods=["POST"])
def contract_add():

    data = request.form.to_dict()
    print(data)
    title = data['title']
    cn_id = data['cn_id']
    #contract_period = data['contract_period']
    contract_start =  data['contract_start']
    contract_end =  data['contract_end']
    #category_id = db.Column(db.String(), nullable=True)
    #atm_id = db.Column(db.String(), nullable=True)
    confidentiality_contract = data['confidentiality_contract']
    agency_reference_id = data['agency_reference_id']
    confidentiality_outputs = data['confidentiality_outputs']
    contract_value = data['contract_value_(aud)']
    #agency_id = db.Column(db.String())
    procurement_method = data['procurement_method']
    description = data['description']
    publish_date = data['publish_date']


    db.create_all()
    contract = Contract(title=title, cn_id=cn_id, contract_start=contract_start, contract_end=contract_end, confidentiality_contract=confidentiality_contract, agency_reference_id=agency_reference_id, confidentiality_outputs=confidentiality_outputs, contract_value=contract_value, procurement_method=procurement_method, description=description, publish_date=publish_date)
    db.session.add(contract)
    db.session.commit()

    response = contract_schema.dump(contract).data
    return response






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
        return jsonify(result)
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

            return api_response('Success - All unspscs Added', None)
        else:
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

@app.route("/agency")
def agency():
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
    
    agency = Agency.query.filter_by(title=title).first()
    if agency==None:
        db.create_all()
        agency = Agency(title=title)
        db.session.add(agency)
        db.session.commit()

        response = agency_schema.dump(agency).data
        return api_response('Success - Agency Added', response)
    else:
        response = agency_schema.dump(agency).data
        return api_response('Success - Agency Already Exists', response)













@app.route("/comments")
def comments():

    comment = Comment.query.all()
    result = comments_schema.dumps(comment).data
    response= {
        'data': result,
        'status_code' : 202
        }
    return jsonify(result)


# ------------  UNSPSC ---------------






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
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
print(db)
from models import User, UserSchema, Comment, CommentSchema, Op, OpSchema, Unspsc, UnspscSchema, UnspscSchemaSimple, Page, Tag





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


@app.route("/")
def hello():
    db.create_all()

    #page = Page()
    #tag = Tag()
    #page.tags.append(tag)
    #db.session.add(page)

    opportunity=Op.query.filter_by(id=240).first()
    category = Unspsc.query.filter_by(id=224).first()
    opportunity.categories.append(category)
    db.session.add(opportunity)

    db.session.commit()

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
        return api_response('Success', result)
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
def get_user_details():

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
        opportunities=Op.query.all()
        result = ops_schema.dump(opportunities).data
        return api_response('Success', result)
    except Exception as e:
	    return(str(e))



@app.route("/op/add", methods=["POST"])
def op_add():
    try:
        data = request.form.to_dict()
        atm_id = data['atm_id']
        unspsc = data['unspsc']

        obj=Op.query.filter_by(atm_id=atm_id).first()
        if obj==None:

            db.create_all()
            opportunity = Op(title=data['title'], atm_id=atm_id)
            #comment = Comment(title="Fight Club", user=user)
            db.session.add(opportunity)
            #data = opportunity
            #db.session.add(comment)
            db.session.commit()

            response = op_schema.dump(opportunity).data
            return api_response('Success - Added Opportunity', response)
        else:
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



# ------------  UNSPSC ---------------

@app.route("/unspsc")
def unspsc():
    try:
        filter_null = bool(request.args.get('filter_null'))
        if filter_null==True:
            # only show results that have a null title
            unspsc=Unspsc.query.filter_by(title='NULL').all()
        else:
            unspsc=Unspsc.query.all()

        result = unspscs_schema.dump(unspsc).data  # THIS SHOWS ALL OF THE Ops FOR THE UNSPSCs
        #result = unspscs_simple_schema.dump(unspsc).data
        return api_response('Success', result)


        #return  jsonify([e.serialize() for e in unspsc])
    except Exception as e:
	    return(str(e))


@app.route("/unspsc/add/<unspsc>")
def unspsc_add(unspsc):
    try:
        obj=Unspsc.query.filter_by(unspsc=unspsc).first()
        if obj==None:

            segment_ = str(unspsc)[:-6] + "000000"
            family_ = str(unspsc)[:-4] + "0000"
            class_ = str(unspsc)[:-2] + "00"
            commodity_ = str(unspsc)

            output = {
                1:{'level':'segment', 'unspsc':segment_, 'parent':0},
                2:{'level':'family', 'unspsc':family_, 'parent':segment_},
                3:{'level':'class', 'unspsc':class_, 'parent':family_},
                4:{'level':'commodity', 'unspsc':commodity_, 'parent':class_}
                }

            for key, value in output.items():
                print key, value['parent'], value['level'], value['unspsc']
                if value['level']!="segment": 
                    obj=Unspsc.query.filter_by(unspsc=value['parent']).first()
                    parent_id = obj.id
                else:
                    parent_id=0

                obj_temp=Unspsc.query.filter_by(unspsc=value['unspsc']).first()
                if obj_temp==None:
                    db.create_all()
                    unspsc = Unspsc(unspsc=value['unspsc'], title='NULL', level=value['level'], parent_id=parent_id)
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
            update({Unspsc.title: title}, synchronize_session=False)
        db.session.commit()
        return api_response('Success - UNSPSC title updated', None)

    except Exception as e:
	    return(str(e))
















@app.route("/comments")
def comments():

    comment = Comment.query.all()
    result = comments_schema.dumps(comment).data
    response= {
        'data': result,
        'status_code' : 202
        }
    return jsonify(response)




@app.route("/op/addSSD", methods=["POST"])
def op_addOLS():
    try:
        data = request.form.to_dict()

        atm_id = data['atm_id']
        unspsc_ = data['unspsc']

        output = {}
        unspsc_search = True # continue to loop through and search all children
        unspsc = Unspsc.query.filter_by(unspsc=unspsc_).first()
        # Loop through all of the parent UNSPSCs
        output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id}
        while unspsc_search==True:
            if unspsc.parent_id!=0:
                unspsc=Unspsc.query.filter_by(id=unspsc.parent_id).one()
                output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id}
            else:
                unspsc_search = False





        
        unspscid_segment = output['segment']['id']
        #return unspsc_dict
        try:
            unspscid_family = output['family']['id']
        except:
            unspscid_family = "NULL"
        
        try:
            unspscid_class = output['class']['id']
        except:
            unspscid_class = "NULL"
        
        try:
            unspscid_commodity = output['commodity']['id']
        except:
            unspscid_commodity = "NULL" 

        


        # Check if the opportunity has already been added
        obj=Opportunity.query.filter_by(atm_id=atm_id).first()
        if obj==None:
            opportunity=Opportunity(
                atm_id = atm_id,
                title = data['title'],
                unspscid_segment = None,
                #unspscid_family = unspscid_family,
                #unspscid_class = unspscid_class,
                #unspscid_commodity = unspscid_commodity,
            )
            db.session.add(opportunity)
            db.session.commit()
            return "Opportunity added. Opportunity id={}".format(opportunity.id)
        else:
            return "Opportunity already exists."

    except Exception as e:
	    return(str(e))






# ------------  UNSPSC ---------------


@app.route("/unspsc/<unspsc_>")
def unspsc_detail(unspsc_):
    try:
        output = {}
        unspsc_search = True # continue to loop through and search all children
        unspsc=Unspsc.query.filter_by(unspsc=unspsc_).first()
        if unspsc!=None:
            # Loop through all of the parent UNSPSCs
            output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id}
            while unspsc_search==True:
                if unspsc.parent_id!=0:
                    unspsc=Unspsc.query.filter_by(id=unspsc.parent_id).one()
                    output[unspsc.level] = {'id':unspsc.id, 'unspsc':unspsc.unspsc, 'title':unspsc.title, 'parent_id':unspsc.parent_id}
                else:
                    unspsc_search = False
        else:
            output = {'response': False}
        return jsonify(output)
    except Exception as e:
	    return(str(e))




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
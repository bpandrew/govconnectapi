import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print(db)
from models import Book, User, Opportunity, Unspsc

@app.route("/")
def hello():
    return "Hello World!!"

@app.route("/add")
def add_book():
    name=request.args.get('name')
    author=request.args.get('author')
    published=request.args.get('published')
    try:
        book=Book(
            name=name,
            author=author,
            published=published
        )
        db.session.add(book)
        db.session.commit()
        return "Book added. book id={}".format(book.id)
    except Exception as e:
	    return(str(e))

@app.route("/getall")
def get_all():
    try:
        books=Book.query.all()
        return  jsonify([e.serialize() for e in books])
    except Exception as e:
	    return(str(e))

@app.route("/get/<id_>")
def get_by_id(id_):
    try:
        book=Book.query.filter_by(id=id_).first()
        return jsonify(book.serialize())
    except Exception as e:
	    return(str(e))





# ------------  USERS ---------------

@app.route("/users")
def users():
    try:
        users=User.query.all()
        return  jsonify([e.serialize() for e in users])
    except Exception as e:
	    return(str(e))


@app.route("/users/add")
def users_add():
    first_name=request.args.get('first_name')
    last_name=request.args.get('last_name')
    email=request.args.get('email')
    try:
        user=User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(user)
        db.session.commit()
        return "User added. user id={}".format(user.id)
    except Exception as e:
	    return(str(e))


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
@app.route("/op/temp")
def opportunities_temp():
    try:
        opportunity = Opportunity.query.filter_by(id=8).one()
        #return str(opportunity)
        category = Unspsc.query.filter_by(id=83)

        opportunity.categories.append(category)

    except Exception as e:
	    return(str(e))


@app.route("/op")
def opportunities():
    try:
        try:
            page = int(request.args.get('page'))
        except:
            page = 1
        # paginate(Page_no, Results_Per_Page, False)
            #record_query = Opportunity.query.paginate(page, 1000, False)
            #total = record_query.total
            #opportunities = record_query.items
        #return str(opportunities)
        opportunities=Opportunity.query.all()
        #return str(type(opportunities))
        return str([e.serialize() for e in opportunities])
    except Exception as e:
	    return(str(e))


@app.route("/op/add", methods=["POST"])
def opportunities_add():
    try:
        data = request.form.to_dict()

        atm_id = data['atm_id']
        unspsc_ = data['unspsc']

        # get the unspsc category dictionary
        #unspsc_dict = unspsc_detail(unspsc)
 



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


@app.route("/op/delete/<id_>")
def opportunities_delete(id_):
    try:
        obj=Opportunity.query.filter_by(id=id_).one()
        db.session.delete(obj)
        db.session.commit()
        return "Opportunity deleted. Opportunity id={}".format(id_)
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

        return  jsonify([e.serialize() for e in unspsc])
    except Exception as e:
	    return(str(e))

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

@app.route("/unspsc/add", methods=["POST"])
def unspsc_add():
    try:
        data = request.form.to_dict()
        unspsc = data['unspsc']
        title = data['title']
        level = data['level']

        obj=Unspsc.query.filter_by(unspsc=unspsc).first()
        if obj==None:

            # find the parent
            if level!='segment': # if it is a segment, it has no parent
                if level=='family':
                    unspsc_parent = unspsc[:-6] + "000000"
                elif level=='class':
                    unspsc_parent = unspsc[:-4] + "0000"
                elif level=='commodity':
                    unspsc_parent = unspsc[:-2] + "00"
                #return unspsc_parent
                obj=Unspsc.query.filter_by(unspsc=unspsc_parent).first()
                parent_id = obj.id
            else:
                parent_id = 0

            unspsc=Unspsc(
                unspsc=unspsc,
                title=title,
                level=level,
                parent_id=parent_id
            )

            db.session.add(unspsc)
            db.session.commit()
            return "UNSPSC added. UNSPSC id={}".format(unspsc.id)
        else:
            return "UNSPSC exists. UNSPSC id={}".format(obj.id)

    except Exception as e:
	    return(str(e))


@app.route("/unspsc/title")
def unspsc_title():
    try:
        title = request.args.get('title').capitalize()
        unspsc = int(request.args.get('unspsc'))

        db.session.query(Unspsc).filter(Unspsc.unspsc == unspsc).\
            update({Unspsc.title: title}, synchronize_session=False)
        db.session.commit()
        output = {'response': 'Success'}
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
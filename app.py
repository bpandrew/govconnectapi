import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print(db)
from models import Book, User, Opportunity

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

@app.route("/op")
def opportunities():
    try:
        try:
            page = int(request.args.get('page'))
        except:
            page = 1
        # paginate(Page_no, Results_Per_Page, False)
        record_query = Opportunity.query.paginate(page, 5, False)
        total = record_query.total
        opportunities = record_query.items

        #opportunities=Opportunity.query.all()
        return jsonify([e.serialize() for e in opportunities])
    except Exception as e:
	    return(str(e))


@app.route("/op/add", methods=["POST"])
def opportunities_add():
    try:
        data = request.form.to_dict()

        atm_id = data['atm_id']

        # Check if the opportunity has already been added
        obj=Opportunity.query.filter_by(atm_id=atm_id).first()
        if obj==None:
            opportunity=Opportunity(
                atm_id = atm_id,
                title = data['title']
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


if __name__ == '__main__':
    app.run()
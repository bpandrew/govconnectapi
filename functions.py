    
import hashlib, binascii, os
import humanize
from datetime import datetime, date, time, timedelta
from flask import Flask, request, jsonify, session, redirect, url_for, g, Response


# Hash a password for storing in the database
def hash_password(password):
    h = hashlib.md5(password.encode())
    return h.hexdigest()


# Formats a standard JSON response
def json_response(message, data):
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


# check user logged in
def login_required(token):
    if token==None:
        return redirect(url_for('login'))


# format as a currency
def format_currency(value):
    value = float(value)
    if value<1000000:
        output = "$"+ humanize.intcomma(value) +"0"
        return output
    else:
        output = "$"+ humanize.intword(value)
        return output


# Generate the dates for the current financial year and the previous
def financial_years():
    now = datetime.now()
    if now.month>=7:
        cfy_start = str(now.year)+'-07-01'
        cfy_end = str(now.year+1)+'-06-30'
        lfy_start = str(now.year-1)+'-07-01'
        lfy_end = str(now.year)+'-06-30'
    else:
        cfy_start = str(now.year-1)+'-07-01'
        cfy_end = str(now.year)+'-06-30'
        lfy_start = str(now.year-2)+'-07-01'
        lfy_end = str(now.year-1)+'-06-30'

    if now.month<10:
        month = "0"+str(now.month)
    else:
        month = str(now.month)
    if now.day<10:
        day = "0"+str(now.day)
    else:
        day = str(now.day)
    now_string = str(now.year)+"-"+ month +"-"+ day
    
    return cfy_start, cfy_end, lfy_start, lfy_end, now_string


# Makes an array more easily readable.  Ie. Steve and Bob.  Or.  Steve, Bob and Mary.
def humanise_array(array):
    i=1
    temp_string = ""
    for item in array:
        if i==len(array):
            temp_string = temp_string + item
        elif i==(len(array)-1):
            temp_string=temp_string+ item + " and "
        else:
            temp_string=temp_string+ item + ", "
        i+=1
    return temp_string



def update_contract_unspsc():
    # check if the title is linked to any contracts where the unspsc_id==None
    contract_unspsc = Contract.query.filter_by(unspsc_id=None).all()
    result = ContractSchema(many=True).dump(contract_unspsc).data

    for contract in result:
        temp_title = contract['category_temp_title'].capitalize()
        unspsc = Unspsc.query.filter_by(title=temp_title).all()
        result_unspsc = UnspscSchema(many=True).dump(unspsc).data
        for item in result_unspsc:
            new_unspsc_id = item['id']
            print(contract['id'])
            print(new_unspsc_id)
            print()  
            db.session.query(Contract).filter(Contract.id == contract['id']).\
                update({Contract.unspsc_id: new_unspsc_id}, synchronize_session=False)
            db.session.commit()            
            break
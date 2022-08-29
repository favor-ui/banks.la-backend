from chalice import Chalice, Response
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from random import randint
from datetime import datetime, date, timedelta
import json


app = Chalice(app_name='Apartments')
# app.debug = True


# CUSTOM SERIALIZER FOR HANDLING DATATYPES
# class DecimalEncoder(json.JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, Decimal):
#       return str(obj)
#     return json.JSONEncoder.default(self, obj)

def build_response(statusCode, body=None):
    if body is not None:
        response = {
            "statusCode": statusCode,
            "body": body
                    }
        return response
        

# Function for database
def get_app_db():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ApartmentData')
    return table

# database function call
table = get_app_db()


# Base URI
@app.route('/', cors=True)
def index():
    item = "Welcome to Banks.la Apartments"
    statusCode = 200
    view = build_response(statusCode, item)
    return view


# post apartments
@app.route('/apartmentdata', methods=['POST'], cors=True)
def add_apartment():
    data = app.current_request.json_body

    format = "%Y-%m-%d"
    date2 = date.today()
    today = str(date2)

    # today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    apartmentNumber = str(data['ApartmentNumber'])

    apartment_prefix = data['ApartmentNamePrefix']

    apartmentname = apartment_prefix + apartmentNumber

    time = str(data['MinimumStay']) + 'day(s)'

    response = table.query(
        KeyConditionExpression=Key('ApartmentName').eq(apartmentname)
    )

    result = response.get('Items', None)

    if len(result) == 0:
        item = {
                'ApartmentName':apartmentname,
                'BuildingName':data['BuildingName'],
                'ApartmentType' :data['ApartmentType'],
                'Price_per_Night':data['Price_per_Night'],
                'Caution Fee':data['CautionFee'],
                'Currency':data['Currency'],
                'Features':data['Features'],
                'Floor':data['Floor'],
                'MinimumStay':time,
                'Max Occupants':data["MaxOccupants"],
                'Helpdesk_Contact':data['Helpdesk_Contact'],
                "Maintained": "yes",
                "Cleaned" : "yes",
                "Available": "yes",
                "Paid": "no",
                "Occupied": "no",
                "Booked": "no",
                'Files':data["Files"],
                'Date': today
                }
        try:
            creatItem = table.put_item(Item = item)
            if creatItem:
                statusCode = 201
                reponse = build_response(statusCode, item)
                return reponse
        except Exception as e:
                return {'message': str(e)}

    else:
        statusCode = 404
        item = 'Apartment already uploaded'
        view = build_response(statusCode, item)
        return view


# Get all apartments
@app.route('/all/apartments', methods=['GET'], cors=True)
def get_all_appartment():
    response = table.scan()
    item = response.get('Items', None)

    try:
        if item != []:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'Building has no apartments at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}

# Get apartments in a building
@app.route('/apartments/building', methods=['POST'], cors=True)
def get_all_appartment_building():

    data = app.current_request.json_body

    # name of building
    building = data['BuildingName']

    # Building search function
    response = table.scan()
    data = response.get('Items', [])

    # apartments list
    item = []

    count = 0

    for each in data:
        if each['BuildingName'] == building:
            # populate the apart's list
            item.append(each)
        count += 1

    try:
        if item != []:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'Sorry, Building details not found'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}

    # if apartments != []:
    #     return {'message' : apartments, 'status': 200}
    # else:

    #     return {'message' : 'Sorry, Building details not found'}

#  Get an aprtment by name
@app.route('/apartment/{ApartmentName}', methods=['GET'], cors=True)
def get_book(ApartmentName):
    
    response = table.query(
        KeyConditionExpression=Key('ApartmentName').eq(ApartmentName)
    )
    item = response.get('Items', None)


    try:
        if item != []:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'Sorry, Apartment not found'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}

    # if data != []:

    #     return {'message' : data, 'status': 200}
    # else:
    #     return 
#

@app.route('/apartments/booked', methods=['GET'], cors=True)
def get_all_booked():

    data = app.current_request.json_body

    # Building search function
    response = table.scan()
    result = response.get('Items', [])

    item =  []

    count = 0

    for each in result:
        seen = each["Booked"]
        if seen == "yes":
            item.append(each)
            # print(booked)
        count += 1

    try:
        if len(item) != 0:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'No booking record for now'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
        return {'message': str(e)}

    # if len(booked) != 0:
    #     return {'message' : booked, 'status': 200}
    # else:
    #     return 

@app.route('/apartments/checkedin', methods=['GET'], cors=True)
def get_all_checkedin():

    data = app.current_request.json_body

    # Building search function
    response = table.scan()
    result = response.get('Items', [])

    # apartments list
    item = []

    count = 0

    # return predefined fields
    # check occupancy status == 1 

    for each in result:
        # "Occupied": "no"
        if each["Occupied"] == "yes":
            # populate the apart's list
            item.append(each)
        count += 1


    try:
        if len(item) != 0:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'No Occupants at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
        return {'message': str(e)}
    # if occuppied != []:
    #     return {'message' : occuppied, 'status': 200}
    # else:
    #     return 

@app.route('/apartments/available', methods=['GET'], cors=True)
def get_all_available():

    data = app.current_request.json_body

    # Building search function
    response = table.scan()
    result = response.get('Items', [])

    # apartments list
    item = []

    count = 0

    # return predefined fields
    # check availability status if maintenace, booking and occupancy == 0
    
    for each in result:
        if each['Available'] == 'yes':
            # populate the apart's list
            item.append(each)
        count += 1

    try:
        if len(item) != 0:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'Sorry no rooms available at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}
    # if seen != []:
    #     return {'message' : seen, 'status': 200}
    # else:
    #     return {'message' : 'Sorry no rooms available at the moment'}

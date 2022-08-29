from chalice import Chalice
import boto3
from random import randint
from datetime import datetime, date, timedelta
from boto3.dynamodb.conditions import Key
import geopy
from geopy.geocoders import Nominatim
# import json
# from decimal import Decimal

app = Chalice(app_name='Building')
# app.debug = True



# CUSTOM SERIALIZER FOR HANDLING DATATYPES
# class DecimalEncoder(json.JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, Decimal):
#       return str(obj)
#     return json.JSONEncoder.default(self, obj)



# def build_response(statusCode, body=None):
#     response = {
#         "statusCode": statusCode,
#         "headers": {
#             "Content-Type": "application/json",
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Max-Age": 2592000,
#             "Access-Control-Allow-Methods": "OPTIONS, POST, GET, DELETE, PATCH",
#         }
#     }

#     if body is not None:
#         response["body"] = json.dumps(body, cls = DecimalEncoder)

#     return response


def build_response(statusCode, body=None):
    if body is not None:
        response = {
            "statusCode": statusCode,
            "body": body
                    }
        return response




# Geolocation function
def points(x, y):
    list = [x,y]
    coordinates = ",".join([str(x) for x in list])
    locator = Nominatim(user_agent="app")
    location = locator.reverse(coordinates)
    details = location.raw
    return details

# Function for database
def get_app_db():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('DataForBuilding')
    return table

# database function call
table = get_app_db()


# Base URL
@app.route('/', cors=True)
def index():
    statusCode = 200
    item = 'Welcome to Banks.la Properties'
    result = build_response(statusCode, item)
    return result 

# Buildings function
@app.route("/building_details", methods=["POST"], cors=True)
def postBuildings():

    data = app.current_request.json_body
    
    lat = data["latitude"]
    lon = data["longitude"]
    # points(x, y)
    details = points(lat, lon)

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ran_dom = randint(1, 99999999)

    bid = str(ran_dom).zfill(8)

    hasHall = data["conference_Hall"].lower()

    if hasHall == "":
        statusCode = 404
        Item = {"message": "Please fill yes or no for the status of Conference Hall"}
        result = build_response(statusCode, Item)
        return result
    # if hasHall != "no" or hasHall != "yes":
    #         return {"message": "Please fill yes or no for the status of Conference Hall", "status": 403}

    building_name = data["buildingName"]

    response = table.query(
        KeyConditionExpression=Key('BuildingName').eq(building_name)
    )

    result = response.get('Items', None)

    if  hasHall == "no" and len(result) == 0:

        item = {
                "BuildingId":bid,
                "BuildingType":data["buildingType"],
                "BuildingName" :data["buildingName"],
                "BuildingAddress":data["address"],
                "BuildingStreet":data["street"],
                "email" : data["email"],
                "branchContact" : data["branchContact"],
                "branch" : data["branch"],
                "Star(s)" :  data["Star(s)"],
                "NumberofApartments" : data["apartmentsNumber"],
                "Features" : data["features"],
                "BuildingAddress2" : details["address"],
                "Country" : details["address"]["country"],
                "zipcode" : details["address"]["postcode"],
                "State" : details["address"]["state"],
                "files":data["buildingFiles"],
                "Location" :{
                                "Latitude" : details["lat"],
                                "Longitude" : details["lon"]
                            },
                "DisplayName" : details["display_name"],
                "Reviews":0,
                "Date": today
                }

        createItem = table.put_item(Item = item)

        try:
            if createItem:
                statusCode = 201
                result = build_response(statusCode, item)
                return result
                # return data[0]
        except Exception as e:
            return {'message': str(e)}

        # return {"message": f"Building {building_name}, with Id {bid} is on {data['Street']} has been added successfully, {response}", "status": 200}
    elif  hasHall == "yes" and len(result) == 0:
        item = {
                "BuildingId":bid,
                "BuildingType":data["buildingType"],
                "BuildingName" :data["buildingName"],
                "BuildingAddress":data["address"],
                "BuildingStreet":data["street"],
                "email" : data["email"],
                "branchContact" : data["branchContact"],
                "branch" : data["branch"],
                "Star(s)" :  data["Star(s)"],
                "NumberofApartments" : data["apartmentsNumber"],
                "Features" : data["features"],
                "BuildingAddress2" : details["address"],
                "Country" : details["address"]["country"],
                "zipcode" : details["address"]["postcode"],
                "State" : details["address"]["state"],
                "files":data["buildingFiles"],
                "Location" :{
                                "Latitude" : details["lat"],
                                "Longitude" : details["lon"]
                            },
                "DisplayName" : details["display_name"],
                "Reviews":0,
                "Date": today,
                "Hall_info" :{
                                "ConferenceHall": data["conference_Hall"],
                                "ConferenceCapcity": data["Conference Capcity"]
                            }
                }

        createItem = table.put_item(Item = item)

        try:
            if createItem:
                statusCode = 201
                result = build_response(statusCode, item)
                return result
                # return data[0]
        except Exception as e:
            return {'message': str(e)}

    else:
        statusCode = 404
        item = 'Building already uploaded'
        result = build_response(statusCode, item)
        return result
        # return response
    #     return {"message": f"Building {building_name}, with Id {bid} is on {data['Street']} has been added successfully, {response}", "status": 200}
    # else:
    #     return {'message': 'Building already uploaded'}


@app.route("/building/name", methods=["POST"], cors=True)
def get_building_name():

    data = app.current_request.json_body

    building_name = data["buildingName"]

    try:
        response = table.query(
        KeyConditionExpression=Key('BuildingName').eq(building_name)
        )
    except Exception as e:
            return {'message': str(e)}

    item = response.get('Items', None)

    # try:
    if item != []:
        statusCode = 201
        result = build_response(statusCode, item)
        return result
        # return data[0]
    else:
        statusCode = 404
        item = f"Sorry {building_name} does not exist please"
        result = build_response(statusCode, item)
        return result

    # except Exception as e:
    #         return {'message': str(e)}
        
    # else:
    #     resullt = response['Items']
        
    #     if resullt:
    #         return {"message": f"Welcome to {building_name}, {resullt[0]}","status": True}, 200
    #         # return resullt[0]
    #     else:
    #         return {"message": f"Sorry {building_name} does not exist please"}


@app.route("/building/all", methods=["GET"], cors=True)
def get_all_building():

    response = table.scan()

    item = response.get('Items', None)

    try:
        if item != []:
            statusCode = 201
            result = build_response(statusCode, item)
            return result
            # return data[0]
        else:
            statusCode = 404
            item = {"message": "No buildings at the moment"}
            result = build_response(statusCode, item)
            return result

    except Exception as e:
            return {'message': str(e)}

    # return {"message": f"Please find all the buiildings {response}","status": True}, 200
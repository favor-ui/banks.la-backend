from chalice import Chalice, Response
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from random import randint
from datetime import datetime, date, timedelta
import json

app = Chalice(app_name='Reviews')


def build_response(statusCode, body=None):
    if body is not None:
        response = {
            "statusCode": statusCode,
            "body": body
                    }
        return response


# Function for database
def get_app_db(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table

# database function call
reviews = get_app_db('DataForReviews')
user = get_app_db('BANKS_LA_GENERAL_USER_TABLE')
builds = get_app_db('DataForBuilding')

@app.route('/', cors=True)
def index():
    statusCode = 200
    item = 'Welcome to Banks.la Properties'
    result = build_response(statusCode, item)
    return result


@app.route('/postreviews', methods=['POST'], cors=True)
def post_reviews():
    data = app.current_request.json_body

    # today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userid = data['user_id']
    result = user.query(KeyConditionExpression=Key('user_id').eq(userid))
    getUser = result.get('Items', None)
    
    if len(getUser) == 0:
        statusCode = 404
        item = 'User not found'
        view = build_response(statusCode, item)
        return view

    BuildingName = data['BuildingName']
    result = builds.query(KeyConditionExpression=Key('BuildingName').eq(BuildingName))
    getbuilds = result.get('Items', None)
    
    if len(getbuilds) == 0:
        statusCode = 404
        item = 'Building not found'
        view = build_response(statusCode, item)
        return view

    reviewBody = data['reviewBody']

    if len(reviewBody) == 0 or len(''.join(i for i in data['reviewBody'] if i.isalpha())) < 10:
        statusCode = 404
        item = 'Review field cannot be empty or less than 10 words'
        view = build_response(statusCode, item)
        return view

    
    date2 = date.today()
    today = str(date2)

    ran_dom = randint(1, 99999999)
    ranid = str(ran_dom).zfill(8)
    reviewId = today[0:4] + ranid + today[5:7]

    Username = getUser[0]['first_name']

    checkreviewId = reviews.query(KeyConditionExpression=Key('ReviewId').eq(reviewId))
    foundid = checkreviewId.get('Items', None)

    if len(foundid) == 0:
        item = {
                'ReviewId':reviewId,
                'BuildingName': BuildingName,
                'Useremail':userid,
                'Userename' :Username,
                'Review':reviewBody,
                'ReviewDate': today,
                "type": "blank"
                }
        try:
            creatItem = reviews.put_item(Item = item)
            if creatItem:
            #     user.update_item(
            #             Key={'user_id': userid},
            #             UpdateExpression="set Reviews=:r",
            #             ExpressionAttributeValues={':r':[{'message':reviewBody, 'reviewdate':today, 'reviewid':reviewId}]}, ReturnValues="UPDATED_NEW")

            #     builds.update_item(
            #             Key={'BuildingName': BuildingName},
            #             UpdateExpression="set Reviews=:r",
            #             ExpressionAttributeValues={':r':reviewId}, ReturnValues="UPDATED_NEW")

                statusCode = 201
                reponse = build_response(statusCode, item)
                return reponse
        except Exception as e:
                return {'message': str(e)}
    else:
        statusCode = 404
        item = 'invalid review request'
        view = build_response(statusCode, item)
        return view

# @app.route('/filter/buildingreviews', methods=['POST'], cors=True)
# def post_reviews():
#     data = app.current_request.json_body


@app.route('/all/reviews', methods=['GET'], cors=True)
def get_all_reviews():
    response = reviews.scan()
    item = response.get('Items', None)
    try:
        if item != []:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'No reviews at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}


@app.route('/building/reviews', methods=['POST'], cors=True)
def get_all_available():

    data = app.current_request.json_body

    BuildingName = data['BuildingName']

    # Building search function
    response = reviews.scan()
    result = response.get('Items', [])

    # apartments list
    item = []
    count = 0
    for each in result:
        if each['BuildingName'] == BuildingName:
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
            item = f'Sorry no reviews for the Building {BuildingName}'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}

@app.route('/user/reviews', methods=['POST'], cors=True)
def get_user_review():

    data = app.current_request.json_body

    userid = data['user_id']
    result = user.query(KeyConditionExpression=Key('user_id').eq(userid))
    getUser = result.get('Items', None)

    if len(getUser) == 0:
        statusCode = 404
        item = 'User not found'
        view = build_response(statusCode, item)
        return view

    response = reviews.scan()
    scanreviews = response.get('Items', None)
    # apartments list
    item = []
    count = 0
    for each in scanreviews:
        if each['Useremail'] == userid:
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
            item = 'Sorry you have no reviews at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}
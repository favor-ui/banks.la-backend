from chalice import Chalice, Response
from datetime import datetime, date, timedelta
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
from random import randint
import uuid
from random import randint
import json


app = Chalice(app_name='Bookings')


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


# A date has day 'd', month 'm' and year 'y'
class Date:
    def __init__(self, d, m, y):
        self.d = d
        self.m = m
        self.y = y

monthDays = [31, 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31]
    
# This function counts number of leap yearsbefore the given date
def countLeapYears(d):
    years = d.y
    # Check if the current year needs to be considered for the count of leap years or not
    if (d.m <= 2):
        years -= 1
    # An year is a leap year if it is a multiple of 4, multiple of 400 and not a multiple of 100.
    return int(years / 4) - int(years / 100) + int(years / 400)
    
# This function returns number of days between two given dates
def getDifference(dt1, dt2):
    # COUNT TOTAL NUMBER OF DAYS BEFORE FIRST DATE 'dt1' initialize count using years and day
    n1 = dt1.y * 365 + dt1.d
    # Add days for months in given date
    for i in range(0, dt1.m - 1):
        n1 += monthDays[i]

    # Since every leap year is of 366 days, Add a day for every leap year
    n1 += countLeapYears(dt1)

    # SIMILARLY, COUNT TOTAL NUMBER OF DAYS BEFORE 'dt2'
    n2 = dt2.y * 365 + dt2.d
    for i in range(0, dt2.m - 1):
        n2 += monthDays[i]
    n2 += countLeapYears(dt2)

    # return difference between two counts
    return (n2 - n1)

# convert date to days, month and year 
def convert(da_te):
    strCon = datetime.datetime.strptime(da_te, "%Y-%m-%d")
    day = strCon.day
    month = strCon.month
    year = strCon.year

    ref = [day, month , year]

    return ref

    

date2 = date.today()
today = str(date2)

# database function call
aparts = get_app_db('ApartmentData')
paid = get_app_db('BANKS_LA_TRANSACTIONS_TABLE')
user = get_app_db('BANKS_LA_GENERAL_USER_TABLE')
builds = get_app_db('DataForBuilding')
booking = get_app_db('DataForBookings')


# Base URI
@app.route('/', cors=True)
def index():
    item = "Welcome to Banks.la Apartments"
    statusCode = 200
    view = build_response(statusCode, item)
    return view


# post booking
@app.route('/booking', methods=['POST'], cors=True)
def createBooking():
    data = app.current_request.json_body

    # find user or return not found
    userid = data['user_id']
    result = user.query(KeyConditionExpression=Key('user_id').eq(userid))
    getUser = result.get('Items', None)
    
    if len(getUser) == 0:
        statusCode = 404
        item = 'User not found'
        view = build_response(statusCode, item)
        return view

    # find apartment or return not found
    apartmentname = data['apartmentName']
    result2 = aparts.query(KeyConditionExpression=Key('ApartmentName').eq(apartmentname))
    getApartment = result2.get('Items', None)
    
    if len(getApartment) == 0:
        statusCode = 404
        item = 'Sorry, apartment not available for now'
        view = build_response(statusCode, item)
        return view

    # find stay duration
    startDate = data['checkinDate']
    endDate = data['checkoutDate']
    start = convert(startDate)
    end = convert(endDate)
    dt1 = Date(start[0],start[1],start[-1])
    dt2 = Date(end[0],end[1],end[-1])
    totaldays = getDifference(dt1, dt2)

    minstaystr = getApartment[0]['MinimumStay'][0]
    minstay = int(minstaystr)
    occupants = data['othervisitors'] + 1
    maxoccupants = getApartment[0]['Max Occupants']
    
    # check booking policies
    if totaldays < minstay:
        statusCode = 403
        item = f'Sorry, Minimum stay is {minstaystr}'
        view = build_response(statusCode, item)
        return view
    
    if occupants > maxoccupants:
        statusCode = 403
        item = f'Sorry, maximum number of occupants is {maxoccupants}, and  been exceeded'
        view = build_response(statusCode, item)
        return view

    # genetate random number for booking   
    ran_dom = randint(1, 99999999)
    ranid = str(ran_dom).zfill(8)
    bookingId = today[0:4] + ranid + str(totaldays)
   
   # check if booking id exist
    checkbookingId = booking.query(KeyConditionExpression=Key('BookingsId').eq(bookingId))
    foundid = checkbookingId.get('Items', None)

    # constants
    pricePernight = getApartment[0]['Price_per_Night']
    cautionFee = getApartment[0]['Caution Fee']

    # payments
    totaldays = getDifference(dt1, dt2)
    bookFee = (pricePernight * totaldays) + cautionFee

    # other details
    stayPeriod = str(getDifference(dt1, dt2)) + "days"
    apartmentFloor = getApartment[0]['Floor']
    buildingname = getApartment[0]['BuildingName']

    Username = getUser[0]['first_name']

    # Generate Booking
    if len(foundid) == 0:
        item = {
                'BookingsId':bookingId,
                'email': data['user_id'],
                'Username': Userename,
                'CheckinDate':data['checkinDate'],
                'CheckoutDate' :data['checkoutDate'],
                'BuildingName' : buildingname,
                'ApartmentName' : apartmentname,
                'Duration' : stayPeriod ,
                'BookingCost': bookFee,
                'ApartmentFlore' : apartmentFloor,
                'Visitors': data['othervisitors'],
                'PricePerNight':pricePernight,
                'CautionFee':cautionFee,
                'Paymentstatus': 'no',
                'valid': 'yes',
                'Booked': 'no',
                'PaymentRef': 'none',
                'BookingDate': today,
                }
        try:
            creatItem = booking.put_item(Item = item)
            if creatItem:
                statusCode = 201
                reponse = build_response(statusCode, item)
                return reponse
        except Exception as e:
                return {'message': str(e)}

    else:
        statusCode = 404
        item = 'Booking record already exist'
        view = build_response(statusCode, item)
        return view


# Get all apartments
@app.route('/all/booking', methods=['GET'], cors=True)
def get_all_activeBooking():
    response = booking.scan()
    item = response.get('Items', None)

    try:
        if item != []:
            statusCode = 201
            view = build_response(statusCode, item)
            return view
            # return data[0]
        else:
            statusCode = 404
            item = 'No bookings at the moment'
            view = build_response(statusCode, item)
            return view
    except Exception as e:
            return {'message': str(e)}


#  Get an aprtment by name
@app.route('/find/{BookingRef}', methods=['GET'], cors=True)
def get_book(BookingRef):
    
    response = booking.query(
        KeyConditionExpression=Key('BookingsId').eq(BookingRef)
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
from datetime import datetime, date, timedelta
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime

# def build_response(statusCode, body=None):
#     if body is not None:
#         response = {
#             "statusCode": statusCode,
#             "body": body
#                     }
#         return response
        

# # Function for database
# def get_app_db(table_name):
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table(table_name)
#     return table


# Python3 program two find number of
# days between two given dates
# A date has day 'd', month 'm' and year 'y'


class Date:
    def __init__(self, d, m, y):
        self.d = d
        self.m = m
        self.y = y

# To store number of days in all months from
# January to Dec.
monthDays = [31, 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31]
    
# This function counts number of leap years
# before the given date
def countLeapYears(d):

    years = d.y

    # Check if the current year needs to be considered
    # for the count of leap years or not
    if (d.m <= 2):
        years -= 1

    # An year is a leap year if it is a multiple of 4,
    # multiple of 400 and not a multiple of 100.
    return int(years / 4) - int(years / 100) + int(years / 400)
    
    
# This function returns number of days between two
# given dates
def getDifference(dt1, dt2):

    # COUNT TOTAL NUMBER OF DAYS BEFORE FIRST DATE 'dt1'

    # initialize count using years and day
    n1 = dt1.y * 365 + dt1.d

    # Add days for months in given date
    for i in range(0, dt1.m - 1):
        n1 += monthDays[i]

    # Since every leap year is of 366 days,
    # Add a day for every leap year
    n1 += countLeapYears(dt1)

    # SIMILARLY, COUNT TOTAL NUMBER OF DAYS BEFORE 'dt2'

    n2 = dt2.y * 365 + dt2.d
    for i in range(0, dt2.m - 1):
        n2 += monthDays[i]
    n2 += countLeapYears(dt2)

    # return difference between two counts
    return (n2 - n1)
 
def convert(da_te):
    strCon = datetime.datetime.strptime(da_te, "%Y-%m-%d")
    day = strCon.day
    month = strCon.month
    year = strCon.year

    ref = [day, month , year]
    return ref

# Driver program
# print(convert("2021-05-21"))

# print(datem.day)        # 2
# print(datem.month)      # 5
# print(datem.year)       # 2021
# print(datem.hour)       # 11
# print(datem.minute)     # 22
# print(datem.second)     # 3


date2 = date.today()
today = str(date2)

# print(today[0:4])

import dateutil.parser

my_date_str = "2011-01-01T16:00:00Z"

dateutil.parser.parse(my_date_str)
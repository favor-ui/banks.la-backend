@app.route('/book/{id}', methods=['PUT'])
def update_book(id):
    data = app.current_request.json_body
    try:
        get_app_db().update_item(Key={
            "id": data['id'],
            "author": data['author']
        },
            UpdateExpression="set title=:r",
            ExpressionAttributeValues={
            ':r': data['title']
        },
            ReturnValues="UPDATED_NEW"
        )
        return {'message': 'ok - UPDATED', 'status': 201}
    except Exception as e:
        return {'message': str(e)}




body = [
        {
            "Occupied": "no",
            "Date": "2022-08-16",
            "ApartmentType": "3 Bedroom Flat",
            "Maintained": "yes",
            "Price_per_Night": 100000.0,
            "Helpdesk_Contact": "0903487652",
            "Floor": 9.0,
            "Max Occupants": 4.0,
            "Cleaned": "yes",
            "Caution Fee": 90000.0,
            "MinimumStay": "5day(s)",
            "Features": "Bedroom:3 Ensuited, Guest Bathroms",
            "Available": "yes",
            "Files": "link",
            "ApartmentName": "M1",
            "Currency": "Naira",
            "BuildingName": "Noah's Court",
            "Paid": "no",
            "Booked": "no"
        }
    ]

price = body[0]["Price_per_Night"]

caution = body[0]["Caution Fee"]

minstaystr = body[0]["MinimumStay"][0]
minsttay = int(minstaystr)

# minstaystr = body[0]["MinimumStay"][0]
# minsttay = int(minstaystr)

# print(minsttay)

maxoccupants = body[0]["Max Occupants"]

date = body[0]["Date"][5:7]

print(date)

# aws cloudformation deploy --template-file /Users/favor/schull/banksla/Reviews/reviews.yaml--stack-name "Reviews"
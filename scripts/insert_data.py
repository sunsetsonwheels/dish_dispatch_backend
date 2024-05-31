from pymongo import MongoClient
from passlib.context import CryptContext
from json import load
from datetime import datetime, timezone

# Prep data for insertion
db = MongoClient("mongodb://dish_dispatch:dish_dispatch@localhost:27017/dish_dispatch").dish_dispatch
crypt_context = CryptContext(schemes=["argon2"], deprecated=["auto"])

data = {"customers": [], "restaurants": []}

with open("scripts/data-gen.json", "r") as f:
    data = load(f)

data["cuisines"] = [data["restaurants"][phone]["cuisine"] for phone in data["restaurants"]]

# Insert users
for customer_phone in data["customers"]:
    customer = data["customers"][customer_phone]
    del customer['membership_number']
    db.customers.insert_one({
        "_id": customer_phone,
        **customer,
        "cart": {},
        "membership": {
            "plan": "monthly",
            "start_date": datetime.now(timezone.utc)
        },
        "password": crypt_context.hash("1234")
    })

# Insert restaurant
for restaurant_phone in data["restaurants"]:
    restaurant = data["restaurants"][restaurant_phone]
    for order in restaurant["orders"]:
        db.orders.insert_one({
            **order,
            "restaurant": restaurant_phone
        })
    del restaurant["orders"]
    db.restaurants.insert_one({
        "_id": restaurant_phone,
        **restaurant,
        "password": crypt_context.hash("1234")
    })


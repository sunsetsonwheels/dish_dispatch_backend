from pymongo import MongoClient

db = MongoClient("mongodb://dish_dispatch:dish_dispatch@localhost:27017/dish_dispatch", tz_aware=True).dish_dispatch
restaurants_col = db.restaurants
customers_col = db.customers
orders_col = db.orders
orders_in_orders_col = db.orders_in_orders
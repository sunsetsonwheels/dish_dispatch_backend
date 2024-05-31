from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from ..models.customers import Customer, CustomerInDB
from ..models.restaurants import RestaurantInDB, Restaurant
from .data import restaurants_col, customers_col

crypt_context = CryptContext(schemes=["argon2"], deprecated=["auto"])
security = HTTPBasic()

def check_customer_auth(credentials: HTTPBasicCredentials) -> Customer:
    customer_raw = customers_col.find_one({"_id": credentials.username})
    if not customer_raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Customer does not exist.")
    customer = CustomerInDB.model_validate(customer_raw)
    if not crypt_context.verify(credentials.password, customer.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong password.")
    return Customer.model_validate(customer_raw)

def check_restaurant_auth(credentials: HTTPBasicCredentials) -> Restaurant:
    restaurant_raw = restaurants_col.find_one({"_id": credentials.username})
    if not restaurant_raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Restaurant does not exist.")
    restaurant = RestaurantInDB.model_validate(restaurant_raw)
    if not crypt_context.verify(credentials.password, restaurant.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong password.")
    return restaurant

def depend_customer(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> Customer:
    return check_customer_auth(credentials)
customer_dependency = Annotated[Customer, Depends(depend_customer)]

def depend_restaurant(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> Restaurant:
    return check_restaurant_auth(credentials)


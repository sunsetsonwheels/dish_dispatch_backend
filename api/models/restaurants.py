from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MenuItem(BaseModel):
    description: str
    price: float


class BaseRestaurant(BaseModel):
    phone: str = Field(..., alias="_id")
    name: str
    cuisine: str

    model_config = ConfigDict(populate_by_name=True)


class Restaurant(BaseRestaurant):
    address: str
    menu: dict[str, MenuItem]

class RestaurantInDB(Restaurant):
    password: str

class RestaurantsResponse(BaseModel):
    restaurants: list[BaseRestaurant]
    cuisines: list[str]

class RestaurantRating(BaseModel):
    average: float
    recent: list[str]

class RestaurantRevenue(BaseModel):
    total: float
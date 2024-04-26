from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MenuItem(BaseModel):
    description: str
    price: float


class OrderStatus(str, Enum):
    preparing = "preparing"
    delivering = "delivering"
    completed = "completed"


class Order(BaseModel):
    items: dict[str, int]
    customer: str
    notes: str | None
    status: OrderStatus


class RestaurantResponse(BaseModel):
    name: str
    address: str
    cuisine: str


class Restaurant(RestaurantResponse):
    menu: dict[str, MenuItem]
    orders: list[Order]


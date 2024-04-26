from fastapi import APIRouter, HTTPException
from ..common.data import data
from ..models.restaurants import RestaurantResponse, Restaurant

router = APIRouter(prefix="/restaurants")

@router.get("/", response_model=dict[str, RestaurantResponse])
def get_restaurants(cuisine: str | None = None):
    restaurant_list = {}
    for phone in data["restaurants"]:
        restaurant = data["restaurants"][phone]
        if cuisine:
            if cuisine != restaurant["cuisine"]:
                continue
        restaurant_list[phone] = RestaurantResponse(
            name=restaurant["name"],
            address=restaurant["address"],
            cuisine=restaurant["cuisine"]
        )
    return restaurant_list

@router.get("/{phone}", response_model=Restaurant, response_model_exclude=["orders"])
def get_restaurant_menu(phone: str):
    if not phone in data["restaurants"]:
        raise HTTPException(404)
    return data["restaurants"][phone]
from fastapi import APIRouter, HTTPException, status, Body, Depends, UploadFile, Form
from ..common.data import restaurants_col, orders_in_orders_col
from ..common.security import depend_restaurant
from ..models.restaurants import RestaurantsResponse, Restaurant, RestaurantRevenue, RestaurantRating
from typing import Annotated
from bson.objectid import ObjectId
from pydantic import Json
from pathlib import Path
from shutil import copyfileobj

router = APIRouter(prefix="/restaurants")

@router.get(
    "/", 
    response_model=RestaurantsResponse, 
    response_model_by_alias=False
)
def get_restaurants(cuisine: str | None = None, name: str | None = None):
    filter = {}
    if cuisine:
        filter["cuisine"] = cuisine
    if name:
        filter["name"] = {
            "$regex": name,
            "$options": "i"
        }
    return {
        "restaurants": list(restaurants_col.find(filter, {"menu": False, "address": False})),
        "cuisines": list(restaurants_col.aggregate([
            {
                "$group": {
                    "_id": None,
                    "cuisines": {
                        "$addToSet": "$cuisine"
                    }
                }
            },
            {
                "$project": {
                    "_id": None,
                    "cuisines": {
                        "$sortArray": {
                            "input": "$cuisines",
                            "sortBy": 1
                        }
                    }
                }
                
            }
        ]))[0]["cuisines"]
    }



@router.get("/{phone}", response_model=Restaurant, response_model_by_alias=False)
def get_restaurant_details(phone: str):
    restaurant_dict = restaurants_col.find_one({"_id": phone})
    if not restaurant_dict:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return restaurant_dict

@router.patch("/{phone}", status_code=status.HTTP_204_NO_CONTENT)
def patch_restaurant(restaurant: Restaurant, auth: Annotated[Restaurant, Depends(depend_restaurant)]):
    restaurants_col.update_one({"_id": auth.phone}, {"$set": restaurant.model_dump(by_alias=True, exclude=["password"])})
    for img in Path(f'api/static/imgs/{restaurant.phone}').iterdir():
        if img.stem != "hero" or img.stem not in restaurant.menu:
            img.unlink(missing_ok=True)

@router.put("/{phone}", status_code=status.HTTP_204_NO_CONTENT)
def put_menu_photo(file: UploadFile, name: Annotated[str, Form()], restaurant: Annotated[Restaurant, Depends(depend_restaurant)]):
    res_folder = Path(f'api/static/imgs/{restaurant.phone}')
    res_folder.mkdir(exist_ok=True)
    with open(res_folder / f'{name}.jpg', "wb") as img:
        copyfileobj(file.file, img)

@router.get("/{phone}/stats/rating", response_model=RestaurantRating)
def get_rating(phone: str):
    ratings = list(orders_in_orders_col.aggregate([
        {
            '$match': {
                'restaurant.phone': phone
            }
        }, {
            '$group': {
                '_id': '$restaurant.phone', 
                'average': {
                    '$avg': '$review.rating'
                }, 
                'recent': {
                    '$addToSet': '$review.comment'
                }
            }
        }, {
            '$set': {
                'recent': {
                    '$slice': [
                        '$recent', 3
                    ]
                }
            }
        }
    ]))
    if len(ratings) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return ratings[0]

@router.get("/{phone}/stats/revenue", response_model=RestaurantRevenue)
def get_revenue(phone: str, restaurant: Annotated[Restaurant, Depends(depend_restaurant)]):
    if restaurant.phone != phone:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not logged in for restaurant.")
    revenues = list(orders_in_orders_col.aggregate([
        {
            '$match': {
                'restaurant.phone': phone
            }
        }, {
            '$project': {
                'phone': '$restaurant.phone', 
                'items': {
                    '$objectToArray': '$items'
                }
            }
        }, {
            '$unwind': {
                'path': '$items'
            }
        }, {
            '$group': {
                '_id': '$phone', 
                'total': {
                    '$sum': '$items.v.price'
                }
            }
        }
    ]))
    if len(revenues) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return revenues[0]
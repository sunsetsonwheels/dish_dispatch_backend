from fastapi import APIRouter, Depends, status, Body, HTTPException
from ..common.security import depend_restaurant
from ..common.data import orders_col, orders_in_orders_col
from ..models.orders import OrderInOrder, OrderStatus, BaseOrderInOrder
from ..models.restaurants import Restaurant
from typing import Annotated
from bson import ObjectId

router = APIRouter(prefix="/orders")

@router.get(
    "/restaurant", 
    response_model=list[BaseOrderInOrder], 
    response_model_by_alias=False, 
    response_model_exclude_none=True
)
def get_restaurant_orders(restaurant: Annotated[Restaurant, Depends(depend_restaurant)]):
    return orders_in_orders_col.aggregate([
        {
            '$match': {
                'restaurant.phone': restaurant.phone
            }
        }, {
            '$lookup': {
                'from': 'orders', 
                'localField': 'parent_id', 
                'foreignField': '_id', 
                'as': 'parent'
            }
        }, {
            '$unwind': "$parent"
        }
    ])

@router.get(
    "/restaurant/{id}", 
    response_model=OrderInOrder, 
    response_model_by_alias=False, 
    response_model_exclude_none=True
)
def get_order(id: str, restaurant: Annotated[Restaurant, Depends(depend_restaurant)]):
    orders_dict = list(orders_in_orders_col.aggregate([
        {
            '$match': {
                '_id': ObjectId(id)
            }
        }, {
            '$lookup': {
                'from': 'orders', 
                'localField': 'parent_id', 
                'foreignField': '_id', 
                'as': 'parent'
            }
        }, {
            '$unwind': "$parent"
        }, {
            "$project": {
                "parent_id": 0
            }
        }
    ]))
    if (len(orders_dict) == 0):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found.")
    order = OrderInOrder.model_validate(orders_dict[0])
    if order.restaurant.phone != restaurant.phone:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not your order.")
    return order

@router.patch("/restaurant/{id}/status", status_code=status.HTTP_204_NO_CONTENT)
def patch_order_status(id: str, status: Annotated[OrderStatus, Body(...)]):
    orders_in_orders_col.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
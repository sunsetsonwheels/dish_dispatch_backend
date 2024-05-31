from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status, HTTPException

from ..common.data import customers_col, orders_col, orders_in_orders_col, restaurants_col
from ..common.security import customer_dependency, depend_customer
from ..models.customers import (Customer, CustomerCreditCard,
                                CustomerMembership)
from ..models.orders import OrderStatus, OrderResponse, BaseOrder, OrderRequest, OrderReview, OrderInOrder, OrderRestaurant
from bson.objectid import ObjectId

router = APIRouter(prefix="/customers")

@router.get(
    "/info",
    response_model=Customer,
    response_model_by_alias=False
)
def get_customer_info(customer: Annotated[Customer, Depends(depend_customer)]):
    return customer

BodyStr = Annotated[str, Body(...)]

@router.patch(
    "/info/phone", 
    status_code=status.HTTP_204_NO_CONTENT, 
    response_class=Response
)
def patch_customer_phone(
    customer: customer_dependency,
    phone: BodyStr
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"_id": phone}})

@router.patch(
    "/info/name", 
    status_code=status.HTTP_204_NO_CONTENT, 
    response_class=Response
)
def patch_customer_name(
    customer: customer_dependency,
    name: BodyStr
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"name": name}})

@router.patch(
    "/info/address",
    status_code=status.HTTP_204_NO_CONTENT, 
    response_class=Response
)
def patch_customer_name(
    customer: customer_dependency,
    address: BodyStr
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"address": address}})

@router.patch(
    "/info/credit_card",
    status_code=status.HTTP_204_NO_CONTENT, 
    response_class=Response
)
def patch_credit_card(
    customer: customer_dependency,
    credit_card: CustomerCreditCard
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"credit_card": credit_card.model_dump()}})

@router.post("/info/membership")
def add_membership(
    membership: CustomerMembership,
    customer: customer_dependency
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"membership": membership.model_dump()}})

@router.delete("/info/membership")
def delete_membership(
    customer: customer_dependency
):
    customers_col.update_one({"_id": customer.phone}, {"$set": {"membership": None}})

@router.get(
    "/orders",
    response_model=list[OrderResponse],
    response_model_by_alias=False,
    response_model_exclude_none=True
)
def get_customer_orders(customer: customer_dependency):
    return orders_col.aggregate([
        {
            "$lookup": {
                "from": "orders_in_orders",
                "localField": "_id",
                "foreignField": "parent_id",
                "as": "related_orders"
            }
        },
        {
            "$project": {
                "related_orders.parent_id": False
            }
        }
    ])

@router.get(
    "/orders/{id}",
    response_model=OrderResponse,
    response_model_by_alias=False
)
def get_order_details(id: str, customer: customer_dependency):
    order_dicts = list(orders_col.aggregate([
        {
            "$match": {
                "_id": ObjectId(id)
            }
        },
        {
            "$lookup": {
                "from": "orders_in_orders",
                "localField": "_id",
                "foreignField": "parent_id",
                "as": "related_orders"
            }
        },
        {
            "$project": {
                "related_orders.parent_id": False
            }
        }
    ]))
    if len(order_dicts) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No matching order found.")
    order = OrderResponse.model_validate(order_dicts[0])
    if order.customer_phone != customer.phone:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="This is not your order.")
    return order

@router.patch(
    "/orders/{order_id}/{in_order_id}/rate",
    status_code=status.HTTP_204_NO_CONTENT
)
def rate_order(order_id: str, in_order_id: str, review: OrderReview, customer: customer_dependency):
    filter = {"_id": ObjectId(in_order_id)}
    order_in_order_dict = orders_in_orders_col.find_one(filter)
    if not order_in_order_dict:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No matching order found.")
    order_in_order = OrderInOrder.model_validate(order_in_order_dict)
    if order_in_order.parent_id != order_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Parent order ID doesn't match.")
    order_dict = orders_col.find_one({"_id": ObjectId(order_in_order.parent_id)})
    if not order_dict:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No matching parent order found.")
    order = BaseOrder.model_validate(order_dict)
    if order.customer_phone != customer.phone:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="This is not your order.")
    orders_in_orders_col.update_one(filter, {
        "$set": {
            "review": review.model_dump()
        }
    })

@router.post(
    "/orders"
)
def submit_order(
    order: OrderRequest,
    customer: customer_dependency
):
    if customer.phone != order.customer_phone:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Customer phone number mismatch.")
    result = orders_col.insert_one(
        order.model_dump(
            by_alias=True, exclude_none=True, exclude=["id", "summary.subtotal_surcharge", "summary.total", "cart"]
        )
    )
    for restaurant in order.cart:
        restaurant_dict = restaurants_col.find_one({"_id": restaurant})
        if not restaurant_dict:
            orders_col.delete_one({"_id": result.inserted_id})
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Restaurant {restaurant} does not exist.")
        total = 0.0
        for name in order.cart[restaurant]:
            item = order.cart[restaurant][name]
            total += item.price * item.quantity
        order_restaurant = OrderRestaurant(phone=restaurant_dict['_id'], name=restaurant_dict['name'])
        orders_in_orders_col.insert_one(OrderInOrder(total=total, parent_id=result.inserted_id, restaurant=order_restaurant, items=order.cart[restaurant]).model_dump(by_alias=True, exclude_none=True, exclude="_id"))

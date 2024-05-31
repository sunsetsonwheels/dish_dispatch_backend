from pydantic import BaseModel, Field, computed_field, BeforeValidator, ConfigDict
from enum import Enum
from .customers import Customer
from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId


class OrderStatus(str, Enum):
    pending = "pending"
    rejected = "rejected"
    preparing = "preparing"
    shipping = "shipping"
    completed = "completed"


class OrderReview(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    comment: str


class OrderCartItem(BaseModel):
    price: float
    quantity: int = Field(..., ge=1)

class OrderSummary(BaseModel):
    subtotal: float
    surcharge: float
    @computed_field
    @property
    def subtotal_surcharge(self) -> float:
        return self.subtotal * self.surcharge
    @computed_field
    @property
    def total(self) -> float:
        return self.subtotal_surcharge + self.subtotal
    
class OrderDeliveryInfo(BaseModel):
    phone: str
    name: str
    address: str
    
PyObjectId = Annotated[str, BeforeValidator(str)]

class BaseOrder(BaseModel):
    id: PyObjectId | None = Field(None, alias="_id")
    summary: OrderSummary
    notes: str | None = None
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Customer
    delivery_info: OrderDeliveryInfo
    customer_phone: str
    used_membership: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

class OrderRequest(BaseOrder):
    cart: dict[str, dict[str, OrderCartItem]] = {}

class OrderRestaurant(BaseModel):
    phone: str
    name: str

class BaseOrderInOrder(BaseModel):
    id: PyObjectId | None = Field(None, alias="_id")
    total: float
    status: OrderStatus = OrderStatus.pending
    review: OrderReview | None = None

    @computed_field
    @property
    def date(self) -> datetime:
        return ObjectId(self.id).generation_time

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)


class OrderInOrder(BaseOrderInOrder):
    parent_id: PyObjectId | None = None
    parent: BaseOrder | None = None
    restaurant: OrderRestaurant
    items: dict[str, OrderCartItem]


class OrderResponse(BaseOrder):
    related_orders: list[OrderInOrder] = []

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from datetime import datetime

CustomerCart = dict[str, dict[str, int]]


class CustomerCreditCard(BaseModel):
    number: str
    code: str
    expiry: str


class CustomerMembershipPlan(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class CustomerMembership(BaseModel):
    plan: CustomerMembershipPlan = CustomerMembershipPlan.monthly
    start_date: datetime


class Customer(BaseModel):
    phone: str = Field(..., alias="_id")
    name: str
    address: str
    credit_card: CustomerCreditCard
    membership: CustomerMembership | None = None
 
    model_config = ConfigDict(populate_by_name=True)


class CustomerInDB(Customer):
    password: str

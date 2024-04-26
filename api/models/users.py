from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    membership_number: int = Field(..., alias="_id")
    name: str
    phone: str
    address: str
    credit_card: str
    password: str
 
    model_config = ConfigDict(populate_by_name=True)

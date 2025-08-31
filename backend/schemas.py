from pydantic import BaseModel
from datetime import datetime

class OrderBase(BaseModel):
    item: str
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    status: str

class OrderRead(OrderBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

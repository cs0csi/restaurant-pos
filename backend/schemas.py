from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ----- MENU -----
class MenuItemBase(BaseModel):
    name: str
    price: float
    category: Optional[str] = None
    description: Optional[str] = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class MenuItemRead(MenuItemBase):
    id: int

    class Config:
        from_attributes = True


# ----- ORDER ITEMS -----
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


# ----- ORDERS -----
class OrderBase(BaseModel):
    status: Optional[str] = "pending"


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


# --- MODIFICATION: Added schema for partial updates (e.g., status-only) ---
class OrderUpdate(BaseModel):
    status: Optional[str] = None


class OrderRead(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: Optional[datetime] = None
    items: List[OrderItemRead]

    class Config:
        from_attributes = True
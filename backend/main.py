from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
# MODIFICATION: get_db is now correctly imported from database.py
from database import engine, Base, get_db 
from models import MenuItem, Order, OrderItem

# MODIFICATION: Import the entire module as 'schemas'
import schemas 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant POS API 🍽️")


# --- Root Endpoint ---
@app.get("/")
def root():
    return {"message": "Restaurant POS API running 🚀"}


# --- MENU CRUD ---
@app.post("/menu/", response_model=schemas.MenuItemRead)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/menu/", response_model=list[schemas.MenuItemRead])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()


@app.put("/menu/{item_id}", response_model=schemas.MenuItemRead)
def update_menu_item(item_id: int, item: schemas.MenuItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_item)
    db.commit()
    return {"message": f"Menu item {item_id} deleted successfully"}


# --- ORDERS CRUD ---
@app.post("/orders/", response_model=schemas.OrderRead)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(status=order.status)
    db.add(db_order)
    db.flush()
    
    total_price = 0.0

    for item_data in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            db.rollback() 
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menu_item_id} not found")

        item_price = menu_item.price * item_data.quantity
        total_price += item_price

        db_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item_data.menu_item_id,
            quantity=item_data.quantity,
            price=item_price
        )
        db.add(db_item)

    db_order.total_price = total_price
    
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders/", response_model=list[schemas.OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.get("/orders/{order_id}", response_model=schemas.OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@app.put("/orders/{order_id}", response_model=schemas.OrderRead)
def replace_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db_order.status = order.status
    
    # Delete existing order items (for full replacement logic)
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete(synchronize_session='fetch')
    
    total_price = 0.0
    
    # Add new order items
    for item_data in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menu_item_id} not found")

        item_price = menu_item.price * item_data.quantity
        total_price += item_price
        
        db_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item_data.menu_item_id,
            quantity=item_data.quantity,
            price=item_price
        )
        db.add(db_item)

    db_order.total_price = total_price

    db.commit()
    db.refresh(db_order)
    return db_order


# --- MODIFICATION: Added PATCH endpoint for partial updates (e.g., status) ---
@app.patch("/orders/{order_id}", response_model=schemas.OrderRead)
def update_order_status(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Use model_dump(exclude_unset=True) to only update fields present in the request body
    update_data = order_update.model_dump(exclude_unset=True) 

    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    # If the total_price calculation is affected by status (e.g., discounting on completion), 
    # you'd add logic here. For simple status change, no further calculation is needed.
    
    db.commit()
    db.refresh(db_order)
    return db_order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return {"message": f"Order {order_id} deleted successfully"}
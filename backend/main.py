from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Order
import schemas
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Restaurant POS API running 🚀"}


# --- READ ALL ---
@app.get("/orders/", response_model=list[schemas.OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


# --- CREATE ---
@app.post("/orders/", response_model=schemas.OrderRead)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# --- UPDATE (PUT) ---
@app.put("/orders/{order_id}", response_model=schemas.OrderRead)
def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db_order.item = order.item
    db_order.quantity = order.quantity
    db.commit()
    db.refresh(db_order)
    return db_order


# --- DELETE ---
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(db_order)
    db.commit()
    return {"message": f"Order {order_id} deleted successfully"}

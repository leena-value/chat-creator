from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import uuid4

app = FastAPI(title="Restaurant API")

# Models
class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer_name: str

class Order(BaseModel):
    id: str
    items: List[OrderItem]
    customer_name: str
    total: float
    status: str = "pending"

# In-memory storage
menu_items = {
    "1": MenuItem(id="1", name="Pizza Margherita", description="Classic tomato and mozzarella pizza", price=10.99),
    "2": MenuItem(id="2", name="Burger", description="Beef burger with cheese and fries", price=12.50),
    "3": MenuItem(id="3", name="Caesar Salad", description="Fresh salad with chicken and Caesar dressing", price=8.99),
    "4": MenuItem(id="4", name="Pasta Carbonara", description="Creamy pasta with bacon", price=11.50),
    "5": MenuItem(id="5", name="Tiramisu", description="Italian coffee-flavored dessert", price=6.99),
}

orders: Dict[str, Order] = {}

# Routers
menu_router = APIRouter(prefix="/menu", tags=["menu"])
order_router = APIRouter(prefix="/orders", tags=["orders"])

# Menu endpoints
@menu_router.get("/", response_model=List[MenuItem])
async def get_menu():
    return list(menu_items.values())

@menu_router.get("/{item_id}", response_model=MenuItem)
async def get_menu_item(item_id: str):
    if item_id not in menu_items:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_items[item_id]

# Order endpoints
@order_router.post("/", response_model=Order)
async def create_order(order_data: OrderCreate):
    # Validate all menu items exist
    for item in order_data.items:
        if item.menu_item_id not in menu_items:
            raise HTTPException(status_code=400, detail=f"Menu item with id {item.menu_item_id} not found")
    
    # Calculate total
    total = 0
    for item in order_data.items:
        menu_item = menu_items[item.menu_item_id]
        total += menu_item.price * item.quantity
    
    # Create order
    order_id = str(uuid4())
    new_order = Order(
        id=order_id,
        items=order_data.items,
        customer_name=order_data.customer_name,
        total=round(total, 2)
    )
    
    orders[order_id] = new_order
    return new_order

@order_router.get("/", response_model=List[Order])
async def get_orders():
    return list(orders.values())

@order_router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@order_router.put("/{order_id}", response_model=Order)
async def update_order(order_id: str, order_data: OrderCreate):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate all menu items exist
    for item in order_data.items:
        if item.menu_item_id not in menu_items:
            raise HTTPException(status_code=400, detail=f"Menu item with id {item.menu_item_id} not found")
    
    # Calculate total
    total = 0
    for item in order_data.items:
        menu_item = menu_items[item.menu_item_id]
        total += menu_item.price * item.quantity
    
    # Update order
    orders[order_id].items = order_data.items
    orders[order_id].customer_name = order_data.customer_name
    orders[order_id].total = round(total, 2)
    
    return orders[order_id]

@order_router.delete("/{order_id}")
async def delete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    del orders[order_id]
    return {"message": "Order deleted successfully"}

@order_router.patch("/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "preparing", "ready", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    orders[order_id].status = status
    return {"message": f"Order status updated to {status}"}

# Register routers
app.include_router(menu_router)
app.include_router(order_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Restaurant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
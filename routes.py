from fastapi import APIRouter
from models import Order
from database import orders_db

router = APIRouter()

@router.get("/order-status/{order_id}")
async def get_order_status(order_id: str):
    """Fetch the status of an order by order ID."""
    order = orders_db.get(order_id)
    if order:
        return {"order_id": order_id, "status": order["status"]}
    return {"error": "Order not found"}

@router.post("/create-order/")
async def create_order(order: Order):
    """Create a new order."""
    if order.order_id in orders_db:
        return {"error": "Order ID already exists"}
    
    orders_db[order.order_id] = {
        "customer_name": order.customer_name,
        "item": order.item,
        "status": "Pending"
    }
    return {"message": "Order created successfully", "order_id": order.order_id}

@router.post("/cancel-order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an existing order."""
    if order_id in orders_db:
        orders_db[order_id]["status"] = "Cancelled"
        return {"message": f"Order {order_id} cancelled successfully"}
    return {"error": "Order not found"}

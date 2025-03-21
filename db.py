from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")  # Ensure this is set in .env
client = MongoClient(MONGO_URI)
db = client["orders"]  # Database name
orders_collection = db["Stock_order"]  # Collection name

def get_order_status(order_id: str):
    order = orders_collection.find_one({"_id": order_id})
    return order["status"] if order else "Order not found."

def create_order(order_id: str, customer_name: str, item: str):
    if orders_collection.find_one({"_id": order_id}):
        return "Order already exists."
    
    new_order = {"_id": order_id, "customer_name": customer_name, "item": item, "status": "Pending"}
    orders_collection.insert_one(new_order)
    return "Order created successfully."

def cancel_order(order_id: str):
    order = orders_collection.find_one({"_id": order_id})
    if not order:
        return "Order not found."
    
    if order["status"] == "Canceled":
        return "Order is already canceled."
    
    orders_collection.update_one({"_id": order_id}, {"$set": {"status": "Canceled"}})
    return "Order canceled successfully."

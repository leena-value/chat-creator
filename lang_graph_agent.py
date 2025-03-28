from langchain_openai import AzureChatOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_MODEL_VERSION
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
import requests

# Initialize Model
model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version=OPENAI_MODEL_VERSION,
    temperature=0.5,
    max_tokens=1000,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# ------------------------------
# API Integration Tools
# ------------------------------

# Menu Tools
@tool
def get_menu():
    """Fetch all menu items."""
    url = "http://127.0.0.1:8000/menu"
    response = requests.get(url)
    return response.json()

@tool
def get_menu_item(item_id: str):
    """Fetch details of a specific menu item by ID."""
    url = f"http://127.0.0.1:8000/menu/{item_id}"
    response = requests.get(url)
    if response.status_code == 404:
        return f"Menu item with ID {item_id} not found."
    return response.json()

# Order Tools
@tool
def place_order(order_items: list, customer_name: str):
    """
    Place an order by providing a list of items and a customer name.
    Format: {"items": [{"menu_item_id": "1", "quantity": 2}], "customer_name": "John"}
    """
    url = "http://127.0.0.1:8000/orders"
    payload = {"items": order_items, "customer_name": customer_name}
    response = requests.post(url, json=payload)
    return response.json()

@tool
def get_all_orders():
    """Fetch all orders."""
    url = "http://127.0.0.1:8000/orders"
    response = requests.get(url)
    return response.json()

@tool
def get_order_details(order_id: str):
    """Fetch details of a specific order by ID."""
    url = f"http://127.0.0.1:8000/orders/{order_id}"
    response = requests.get(url)
    if response.status_code == 404:
        return f"Order with ID {order_id} not found."
    return response.json()

@tool
def update_order(order_id: str, order_items: list, customer_name: str):
    """
    Update an existing order.
    Format: {"items": [{"menu_item_id": "1", "quantity": 2}], "customer_name": "John"}
    """
    url = f"http://127.0.0.1:8000/orders/{order_id}"
    payload = {"items": order_items, "customer_name": customer_name}
    response = requests.put(url, json=payload)
    if response.status_code == 404:
        return f"Order with ID {order_id} not found."
    return response.json()

@tool
def delete_order(order_id: str):
    """Delete an order by ID."""
    url = f"http://127.0.0.1:8000/orders/{order_id}"
    response = requests.delete(url)
    if response.status_code == 404:
        return f"Order with ID {order_id} not found."
    return {"message": f"Order {order_id} deleted successfully."}

@tool
def update_order_status(order_id: str, status: str):
    """
    Update an order's status.
    Valid statuses: "pending", "preparing", "ready", "delivered", "cancelled"
    """
    url = f"http://127.0.0.1:8000/orders/{order_id}/status"
    params = {"status": status}
    response = requests.patch(url, params=params)
    if response.status_code == 404:
        return f"Order with ID {order_id} not found."
    if response.status_code == 400:
        return f"Invalid status. Must be one of: pending, preparing, ready, delivered, cancelled."
    return response.json()

# Function to extract user order from input
def parse_order_request(user_message, menu):
    """
    Extract items and quantities from user input.
    Example: "I want 2 burgers and 1 pizza"
    Returns: [{"menu_item_id": "1", "quantity": 2}, {"menu_item_id": "3", "quantity": 1}]
    """
    order_items = []
    menu_dict = {item["name"].lower(): item for item in menu}

    words = user_message.lower().split()
    for name, details in menu_dict.items():
        for i, word in enumerate(words):
            if word == name:
                try:
                    quantity = int(words[i - 1])  # Extract quantity from previous word
                    order_items.append({"menu_item_id": details["id"], "quantity": quantity})
                except ValueError:
                    pass  # Skip if not a valid number
    
    return order_items

# All tools for the Agent
tools = [
    get_menu, 
    get_menu_item,
    place_order, 
    get_all_orders,
    get_order_details,
    update_order,
    delete_order,
    update_order_status
]

# Create Agent Graph
graph = create_react_agent(model, tools=tools)

def print_stream(stream):
    response = None
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
            response = message
    return response

# Initialize chat history
chat_history = []

def extract_customer_info(chat_history):
    """Extract customer name and preferences from chat history."""
    customer_info = {"name": None, "previous_orders": []}
    
    for msg_type, msg_content in chat_history:
        if msg_type == "user" and "my name is" in msg_content.lower():
            # Extract name using a simple heuristic
            name_start = msg_content.lower().find("my name is") + len("my name is")
            name_end = msg_content.find(".", name_start)
            if name_end == -1:
                name_end = len(msg_content)
            customer_info["name"] = msg_content[name_start:name_end].strip()
    
    return customer_info

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break

    # Extract customer info from chat history
    customer_info = extract_customer_info(chat_history)
    
    # Format input with chat history
    messages = []
    
    # Add previous messages from chat history
    for msg_type, msg_content in chat_history:
        if msg_type == "user":
            messages.append(HumanMessage(content=msg_content))
        elif msg_type == "assistant":
            messages.append(AIMessage(content=msg_content))
    
    # Add current user message
    messages.append(HumanMessage(content=user_input))
    
    # Create input with chat history
    input_with_history = {"messages": messages}
    
    print("Bot:")
    response = print_stream(graph.stream(input_with_history, stream_mode="values"))
    
    # Update chat history with the new exchange
    chat_history.append(("user", user_input))
    if response:
        chat_history.append(("assistant", response.content))

# For testing the automated conversation flow (optional)
def simulate_conversation():
    test_messages = [
        HumanMessage(content="Can you show me the menu?"),
        HumanMessage(content="I want to order 2 burgers and 1 pizza."),
        HumanMessage(content="My name is Alex. Confirm my order."),
        HumanMessage(content="Can you check the status of my order?"),
        HumanMessage(content="I'd like to change my order to 1 burger and 2 pizzas.")
    ]
    
    # Process messages one by one to simulate a conversation with history
    all_messages = []
    for msg in test_messages:
        all_messages.append(msg)
        print(f"\nUser: {msg.content}")
        print("Bot:")
        response = print_stream(graph.stream({"messages": all_messages}, stream_mode="values"))
        if response:
            all_messages.append(response)

# Uncomment to run the simulation
# simulate_conversation()
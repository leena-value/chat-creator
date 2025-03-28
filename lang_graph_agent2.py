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

# Tool: Get Menu
@tool
def get_menu():
    """Fetch all menu items."""
    url = "http://127.0.0.1:8000/menu"
    response = requests.get(url)
    return response.json()

# Tool: Place Order
@tool
def place_order(order_items: list, customer_name: str):
    """
    Place an order by providing a list of items and a customer name.
    Ask for customer name explicitly.
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

# Order-Taking Logic
def take_order_logic(user_message, customer_name):
    """
    Handles the order-taking process:
    1. Fetch menu
    2. Extract order details from user input
    3. Confirm and place order
    """
    menu = get_menu()
    order_items = parse_order_request(user_message, menu)
    
    if not order_items:
        return "Sorry, I couldn't understand your order. Please specify item names and quantities."
    
    # Place order
    response = place_order(order_items, customer_name)
    return response

# Tools for the Agent
tools = [get_menu, place_order, get_all_orders]

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

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break

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
        HumanMessage(content="My name is Alex. Confirm my order.")
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
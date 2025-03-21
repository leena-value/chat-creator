import requests
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import AzureChatOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_MODEL_VERSION

# Backend FastAPI URL
BASE_URL = "http://127.0.0.1:8000"

### --- API Call Functions --- ###
def get_order_status(order_id: str):
    """Fetch the status of an order by its order ID."""
    response = requests.get(f"{BASE_URL}/order-status/{order_id}")
    return response.json() if response.status_code == 200 else {"error": response.text}

def create_order(input_text: str):
    """Create a new order. Input format: 'order_id, customer_name, item'."""
    try:
        order_id, customer_name, item = map(str.strip, input_text.split(","))
        payload = {"order_id": order_id, "customer_name": customer_name, "item": item}
        response = requests.post(f"{BASE_URL}/create-order/", json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception:
        return {"error": "Invalid input. Use format: order_id, customer_name, item"}

def cancel_order(order_id: str):
    """Cancel an order using its order ID."""
    response = requests.post(f"{BASE_URL}/cancel-order/{order_id}")
    return response.json() if response.status_code == 200 else {"error": response.text}

### --- Define ReAct Agent Tools --- ###
tools = [
    Tool(name="Get Order Status", func=get_order_status, description="Use when asked about order status."),
    Tool(name="Create Order", func=create_order, description="Use when asked to create an order. Format: 'order_id, customer_name, item'."),
    Tool(name="Cancel Order", func=cancel_order, description="Use when asked to cancel an order."),
]

### --- Initialize the ReAct Agent --- ###
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version=OPENAI_MODEL_VERSION,
    temperature=0.5,
    max_tokens=1000,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # ReAct agent for decision-making
    verbose=True
)

### --- Chatbot Function --- ###
def chatbot_response(user_input):
    """Processes user input and determines which tool to call using the ReAct agent."""
    try:
        response = agent.run(user_input)
        return response
    except Exception as e:
        return f"⚠️ Error processing request: {str(e)}"

from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import AzureChatOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_MODEL_VERSION
from db import create_order, cancel_order, get_order_status

# Initialize Azure OpenAI Model
model = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version=OPENAI_MODEL_VERSION,
    temperature=0.75,
    max_tokens=1000,
    max_retries=5,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Define LangChain Tools
tools = [
    Tool(
        name="Create Order",
        func=create_order,
        description="Creates a new order. Provide order_id, customer_name, and item."
    ),
    Tool(
        name="Cancel Order",
        func=cancel_order,
        description="Cancels an existing order. Provide the order ID."
    ),
    Tool(
        name="Get Order Status",
        func=get_order_status,
        description="Fetches the status of an order. Provide the order ID."
    ),
]

# Initialize ReAct Agent
agent = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def ask_bot(query):
    """Processes user queries and invokes the agent."""
    return agent.invoke(query)  # UPDATED: Using `invoke()` instead of `run()`

import os
from dotenv import load_dotenv
import redis

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_MODEL_VERSION = os.getenv("OPENAI_MODEL_VERSION")

redis_client = redis.Redis(host='localhost', port=6379, db=0)

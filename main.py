from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot import chatbot_response
from routes import router

app = FastAPI()

# CORS Setup (Allow Streamlit Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from routes.py
app.include_router(router)

@app.get("/chatbot/")
async def chatbot(query: str):
    response = chatbot_response(query)
    return {"response": response}

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .data_dynamo import DatasetChatbot

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

chatbot = DatasetChatbot()


class ChatMessage(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/initial-message", response_class=PlainTextResponse)
async def get_initial_message():
    return chatbot.start_conversation()


@app.post("/chat", response_class=PlainTextResponse)
async def chat(message: ChatMessage):
    response = chatbot.process_input(message.message)
    # Here, we're returning the full response from the chatbot,
    # which includes both the action and the message content.
    return response

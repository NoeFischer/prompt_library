from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
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


@app.get("/initial-message")
async def get_initial_message():
    return JSONResponse(content={"message": chatbot.conversation_flow()})


@app.post("/chat")
async def chat(message: ChatMessage):
    response = chatbot.conversation_flow(message.message)
    return JSONResponse(content={"message": response})

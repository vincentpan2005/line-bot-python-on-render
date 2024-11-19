from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = FastAPI()

# 替換為你的Line Bot Channel Access Token和Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)

# 替換為你的dify API Key
DIFY_API_KEY = os.getenv('DIFY_API_KEY', None)
DIFY_BASE_URL = os.getenv('DIFY_BASE_URL', None)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        return {"message": "Invalid signature"}
    return {"message": "OK"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    dify_response = call_dify_api(user_message)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=dify_response)
    )

def call_dify_api(user_message):
    url = DIFY_BASE_URL + "/chat-messages"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": {},
        "query": user_message,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "",
    }
    response = requests.post(url, headers=headers, json=data)
    print(response)
    if response.status_code == 200:
        return response.json().get("answer", [{}])[0].get("text", "Sorry, I couldn't generate a response.")
    else:
        return "Sorry, I encountered an error while generating a response."

@app.get("/")
def read_root():
    return {"Hello": "World"}


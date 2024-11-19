import os
import sys
import requests
import asyncio
from fastapi import FastAPI, Request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest,
    ShowLoadingAnimationRequest
)

app = FastAPI()

# 替換為你的Line Bot Channel Access Token和Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)

# 替換為你的dify API Key
DIFY_API_KEY = os.getenv('DIFY_API_KEY', None)
DIFY_BASE_URL = os.getenv('DIFY_BASE_URL', None)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
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
    reply_token = event.reply_token

    # 傳送讀取中的動畫
    asyncio.create_task(send_loading_animation(reply_token))

    # 調用dify API並傳送結果
    dify_response = call_dify_api(user_message)
    with ApiClient(configuration) as api_client:
        api_instance = MessagingApi(api_client)
        reply_message_request = ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=dify_response)]
        )
        api_instance.reply_message(reply_message_request)

async def send_loading_animation(reply_token):
    with ApiClient(configuration) as api_client:
        api_instance = MessagingApi(api_client)
        loading_animation_request = ShowLoadingAnimationRequest(
            reply_token=reply_token
        )
        api_instance.show_loading_animation(loading_animation_request)

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
        "user": "vincent-dify"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("answer", '')
    else:
        return "Sorry, I encountered an error while generating a response."

@app.get("/")
def read_root():
    return {"Hello": "World"}


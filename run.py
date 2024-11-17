import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from linedify import LineDify

# LINE Bot - Dify Agent Integrator
line_dify = LineDify(
    line_channel_access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None),
    line_channel_secret=os.getenv('LINE_CHANNEL_SECRET', None),
    dify_api_key=os.getenv('DIFY_API_KEY', None),
    dify_base_url=os.getenv('DIFY_BASE_URL', None),
    dify_user=os.getenv('DIFY_USER', None)
)

# FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await line_dify.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/callback")
async def handle_request(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        line_dify.process_request,
        request_body=(await request.body()).decode("utf-8"),
        signature=request.headers.get("X-Line-Signature", "")
    )
    return "ok"

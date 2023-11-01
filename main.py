#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/11/01 14:59:52
@Author  :   lvguanjun
@Desc    :   main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from config import COPILOT_CHAT_ROUTE, COPILOT_CHAT_URL
from utils.client_manger import client_manager
from utils.logger import logger
from utils.proxy import proxy_request
from utils.utils import fake_request, get_copilot_token


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await logger.info("Init client")
    client_manager.init_client()
    yield
    await client_manager.close_client()
    await logger.info("Close client")
    await logger.shutdown()


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(COPILOT_CHAT_ROUTE)
async def proxy(request: Request):
    """
    使用 github token 获取 copilot-chat 的提示接口
    """

    github_token = request.headers.get("Authorization", "")
    github_token = github_token.strip("Bearer ")
    if not github_token:
        return Response(status_code=401, content="Unauthorized")
    status_code, copilot_token = await get_copilot_token(github_token)
    if status_code != 200:
        return Response(status_code=status_code, content=copilot_token)
    copilot_token = copilot_token.get("token")
    headers = {
        "Authorization": f"Bearer {copilot_token}",
        "X-Request-Id": "a213f6b8-1c44-4f32-b8f2-738dbcd19a12",
        "Vscode-Sessionid": "9b7f34a2-45d3-4c00-b123-876f45bc7d8c9847215637890",
        "Vscode-Machineid": (
            "e0ef0c6ace8d45b9b6ee8cb47092ceb5e0ef0c6ace8d45b9b6ee8cb47092ceb5"
        ),
        "Editor-Version": "vscode/1.83.1",
        "Editor-Plugin-Version": "copilot-chat/0.8.0",
        "Openai-Organization": "github-copilot",
        "Openai-Intent": "conversation-panel",
        "Content-Type": "application/json",
        "User-Agent": "GitHubCopilotChat/0.8.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate,br",
        "connection": "close",
    }
    json_data = await request.json()
    messages = json_data["messages"]
    model = json_data.get("model", "copilot-chat")
    is_stream = json_data.get("stream", False)
    # 使用 copilot-chat 原始请求体
    json_data = {
        "messages": messages,
        "model": model,
        "temperature": 0.1,
        "top_p": 1,
        "n": 1,
        "stream": is_stream,
        "intent": True,
    }
    new_request = fake_request("POST", json=json_data, headers=headers)
    res = await proxy_request(new_request, COPILOT_CHAT_URL)
    if is_stream:
        res.headers["content-type"] = "text/event-stream; charset=utf-8"
    return res


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

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
from utils.copilot_proxy_utils import create_json_data, get_fake_headers
from utils.logger import logger
from utils.proxy import proxy_request
from utils.utils import get_copilot_token, pares_url_token


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
async def copilot_proxy(request: Request):
    """
    使用 github token 获取 copilot-chat 的提示接口
    """

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response(status_code=401, content="Unauthorized")
    github_token = auth_header.removeprefix("Bearer ")
    if not github_token:
        return Response(status_code=401, content="Unauthorized")
    get_token_url, github_token = pares_url_token(github_token)
    if github_token is None:
        return Response(
            status_code=403, content=f"{get_token_url} is not allow to get token"
        )
    status_code, copilot_token = await get_copilot_token(github_token, get_token_url)
    if status_code != 200:
        return Response(status_code=status_code, content=copilot_token)

    max_try = 1
    headers = get_fake_headers(github_token)
    headers["Authorization"] = f"Bearer {copilot_token.get('token')}"
    json_data = await create_json_data(request)
    new_request = ("POST", headers, json_data)

    return await proxy_request(new_request, COPILOT_CHAT_URL, max_try)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

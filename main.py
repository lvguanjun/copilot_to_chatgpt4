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
from utils.copilot_proxy_utils import create_headers, create_json_data, get_tokens
from utils.logger import logger
from utils.proxy import proxy_request
from utils.utils import fake_request


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

    status_code, token = await get_tokens(request)
    if status_code != 200:
        return Response(status_code=status_code, content=token)
    max_try = 3
    headers = create_headers(token)
    json_data, is_stream = await create_json_data(request)
    new_request = fake_request("POST", json=json_data, headers=headers)
    res = await proxy_request(new_request, COPILOT_CHAT_URL, max_try)
    if is_stream:
        res.headers["content-type"] = "text/event-stream; charset=utf-8"
    return res


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

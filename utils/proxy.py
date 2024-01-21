#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   proxy.py
@Time    :   2023/11/01 23:53:08
@Author  :   lvguanjun
@Desc    :   proxy.py
"""

import traceback

import httpx
from fastapi import Request, Response
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from config import DEBUG
from utils.client_manger import client_manager
from utils.logger import logger


async def make_request(request: Request, target_url: str) -> httpx.Response:
    json = await request.json()
    req = httpx.Request(request.method, target_url, headers=request.headers, json=json)
    response = await client_manager.client.send(req, stream=True)
    return response


async def stream_response(response: httpx.Response):
    async for line in response.aiter_lines():
        if line:
            yield line + "\n\n"


async def handle_response(response: httpx.Response) -> StreamingResponse | Response:
    is_stream = response.headers.get("transfer-encoding") == "chunked"

    if not is_stream:
        return Response(
            await response.aread(),
            status_code=response.status_code,
            headers=response.headers,
            background=BackgroundTask(close_response, response),
        )

    response.headers["content-type"] = "text/event-stream; charset=utf-8"

    return StreamingResponse(
        stream_response(response),
        status_code=response.status_code,
        headers=response.headers,
        background=BackgroundTask(close_response, response),
    )


async def close_response(response: httpx.Response):
    await response.aclose()
    if DEBUG:
        await logger.debug("Response closed.")


async def log_error(i: int, response: httpx.Response = None, error: Exception = None):
    if response:
        await logger.warning(
            f"{i + 1}th try failed, status code: {response.status_code}"
        )
        if DEBUG:
            await logger.debug(f"response content: {await response.aread()}")
    elif error:
        await logger.error(
            f"{i + 1}th try failed, error: {str(error) or traceback.format_exc()}"
        )


async def proxy_request(
    request: Request, target_url: str, max_try: int = 1
) -> Response | StreamingResponse:
    for i in range(max_try):
        response = None
        try:
            response = await make_request(request, target_url)
            if response.status_code == 200 or i == max_try - 1:
                return await handle_response(response)
            await log_error(i, response=response)
            await close_response(response)
        except Exception as e:
            await log_error(i, error=e)
            if response:
                await close_response(response)
            if i == max_try - 1:
                return Response("Failed to make request", status_code=500)

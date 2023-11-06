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

from utils.client_manger import client_manager
from utils.logger import logger


async def make_request(request: Request, target_url: str) -> httpx.Response:
    headers = dict(request.headers)
    headers.pop("host", None)
    json = await request.json()
    req = client_manager.client.build_request(
        request.method, target_url, headers=headers, json=json
    )
    response = await client_manager.client.send(req, stream=True)
    return response


async def handle_response(response: httpx.Response) -> StreamingResponse:
    streaming_response = StreamingResponse(
        response.aiter_bytes(),
        status_code=response.status_code,
        media_type=response.headers.get("Content-Type"),
        background=BackgroundTask(response.aclose),
    )

    for name, value in response.headers.items():
        streaming_response.headers[name] = value
    return streaming_response


async def proxy_request(
    request: Request, target_url: str, max_try: int = 1
) -> Response | StreamingResponse:
    for i in range(max_try):
        response = None
        try:
            response = await make_request(request, target_url)
            if response.status_code == 200 or i == max_try - 1:
                return await handle_response(response)
            await logger.warning(
                f"{i + 1}th try failed, status code: {response.status_code}"
            )
            await response.aclose()
        except Exception as e:
            tb = traceback.format_exc()
            await logger.error(f"{i + 1}th try failed, error: {e if str(e) else tb}")
            if response:
                await response.aclose()
            if i == max_try - 1:
                return Response("Failed to make request", status_code=500)

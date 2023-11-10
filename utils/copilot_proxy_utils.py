#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot_proxy_utils.py
@Time    :   2023/11/05 11:49:20
@Author  :   lvguanjun
@Desc    :   copilot_proxy_utils.py
"""


from typing import Tuple

from fastapi import Request

from utils.utils import VscodeHeaders, get_copilot_token


async def get_tokens(request: Request) -> Tuple[int, str]:
    github_token = request.headers.get("Authorization", "").strip("Bearer ")
    if not github_token:
        return 401, "Unauthorized"
    status_code, copilot_token = await get_copilot_token(github_token)
    if status_code != 200:
        return status_code, copilot_token
    return 200, copilot_token.get("token")


def create_headers(copilot_token: str) -> dict:
    return {
        "Authorization": f"Bearer {copilot_token}",
        **VscodeHeaders.base_headers(),
    }


async def create_json_data(request: Request) -> Tuple[dict, bool]:
    json_data = await request.json()
    is_stream = json_data.get("stream", False)
    return {
        "messages": json_data.get("messages", []),
        "model": json_data.get("model", "copilot-chat"),
        "temperature": json_data.get("temperature", 0.1),
        "top_p": json_data.get("top_p", 1),
        "n": json_data.get("n", 1),
        "stream": is_stream,
        "intent": True,
    }, is_stream

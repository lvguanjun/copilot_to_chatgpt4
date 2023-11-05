#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot_proxy_utils.py
@Time    :   2023/11/05 11:49:20
@Author  :   lvguanjun
@Desc    :   copilot_proxy_utils.py
"""
import random
import string
from typing import Tuple

from fastapi import Request

from utils.utils import get_copilot_token


async def get_tokens(request: Request) -> Tuple[int, str]:
    github_token = request.headers.get("Authorization", "").strip("Bearer ")
    if not github_token:
        return 401, "Unauthorized"
    status_code, copilot_token = await get_copilot_token(github_token)
    if status_code != 200:
        return status_code, copilot_token
    return 200, copilot_token.get("token")


def gen_hex_str(length: int) -> str:
    return "".join(random.choice(string.hexdigits.lower()) for _ in range(length))


def create_headers(copilot_token: str) -> dict:
    return {
        "Authorization": f"Bearer {copilot_token}",
        "X-Request-Id": f"{gen_hex_str(8)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(12)}",
        "Vscode-Sessionid": f"{gen_hex_str(8)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(25)}",
        "Vscode-Machineid": f"{gen_hex_str(64)}",
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

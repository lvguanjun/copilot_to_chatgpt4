#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot_proxy_utils.py
@Time    :   2023/11/05 11:49:20
@Author  :   lvguanjun
@Desc    :   copilot_proxy_utils.py
"""


from cachetools import TTLCache
from fastapi import Request

from utils.utils import VscodeHeaders

# 最多存30个github token信息，每个token信息存储3天
headers_instance_cache = TTLCache(maxsize=30, ttl=259200)


def get_fake_headers(github_token: str) -> dict:
    if headers_instance := headers_instance_cache.get(github_token):
        return headers_instance.base_headers
    headers_instance = VscodeHeaders(github_token)
    headers_instance_cache[github_token] = headers_instance
    return headers_instance.base_headers


async def create_json_data(request: Request) -> dict:
    json_data = await request.json()
    return {
        "messages": json_data.get("messages", []),
        "model": json_data.get("model", "copilot-chat"),
        "temperature": json_data.get("temperature", 0.1),
        "top_p": json_data.get("top_p", 1),
        "n": json_data.get("n", 1),
        "stream": json_data.get("stream", False),
        "intent": True,
    }

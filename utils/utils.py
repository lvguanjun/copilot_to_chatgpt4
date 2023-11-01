#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/11/01 15:00:47
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import json
from typing import Optional

from fastapi import Request
from fastapi.datastructures import Headers

from utils.client_manger import client_manager
from config import GITHUB_TOKEN_URL
from utils.cache import get_token_from_cache, set_token_to_cache


def fake_request(
    method: str, headers: Optional[dict] = None, json: Optional[dict] = None
) -> Request:
    """
    根据提供的json数据和headers，构造一个request对象
    """

    scope = {
        "method": method,
        "headers": Headers(headers).raw if headers else [],
        "type": "http",
    }
    request = Request(scope)
    request._json = json
    return request


async def get_copilot_token(github_token, get_token_url=GITHUB_TOKEN_URL):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        # 请求 github 接口获取 copilot_token
        headers = {
            "Authorization": f"token {github_token}",
        }
        headers = Headers(headers).raw
        response = await client_manager.client.get(get_token_url, headers=headers)
        if response.status_code != 200:
            return response.status_code, response.text
        copilot_token = response.json()
        # 保存到 cache
        set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token

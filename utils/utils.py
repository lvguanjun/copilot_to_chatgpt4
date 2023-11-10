#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/11/01 15:00:47
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import random
import string
import time
from typing import Optional

from fastapi import Request
from fastapi.datastructures import Headers

from config import GITHUB_TOKEN_URL
from utils.cache import get_token_from_cache, set_token_to_cache
from utils.client_manger import client_manager


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


def gen_hex_str(length: int) -> str:
    return "".join(random.choice(string.hexdigits.lower()) for _ in range(length))


class VscodeHeaders:
    # session id 每 10 分钟更新一次，machine id 每 24 小时更新一次
    last_session_id_time = 0
    update_session_id_time = 600
    last_machine_id_time = 0
    update_machine_id_time = 86400
    _vscode_session_id = None
    _vscode_machine_id = None

    @classmethod
    def _update_id(cls, last_time, update_time, id_attr, id_parts):
        now = int(time.time())
        if now - getattr(cls, last_time) > update_time:
            setattr(cls, last_time, now)
            id_value = "-".join(gen_hex_str(length) for length in id_parts)
            setattr(cls, id_attr, id_value)
        return getattr(cls, id_attr)

    @classmethod
    def vscode_session_id(cls) -> str:
        return cls._update_id(
            "last_session_id_time",
            cls.update_session_id_time,
            "_vscode_session_id",
            [8, 4, 4, 4, 25],
        )

    @classmethod
    def vscode_machine_id(cls) -> str:
        return cls._update_id(
            "last_machine_id_time",
            cls.update_machine_id_time,
            "_vscode_machine_id",
            [64],
        )

    @classmethod
    def base_headers(cls) -> dict:
        return {
            "X-Request-Id": "-".join(
                gen_hex_str(length) for length in [8, 4, 4, 4, 12]
            ),
            "Vscode-Sessionid": cls.vscode_session_id(),
            "Vscode-Machineid": cls.vscode_machine_id(),
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


async def get_copilot_token(github_token, get_token_url=GITHUB_TOKEN_URL):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        # 请求 github 接口获取 copilot_token
        headers = {
            "Authorization": f"token {github_token}",
            **VscodeHeaders.base_headers(),
        }
        headers = Headers(headers).raw
        response = await client_manager.client.get(get_token_url, headers=headers)
        if response.status_code != 200:
            return response.status_code, response.text
        copilot_token = response.json()
        # 保存到 cache
        set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token

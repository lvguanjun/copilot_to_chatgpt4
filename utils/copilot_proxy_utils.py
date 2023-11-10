#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot_proxy_utils.py
@Time    :   2023/11/05 11:49:20
@Author  :   lvguanjun
@Desc    :   copilot_proxy_utils.py
"""


import hashlib
import ipaddress
from typing import Tuple

from fastapi import Request

from config import IS_SHARE, TOKEN_POOL, g_token_pool, g_token_pool_errors, TOKEN_MAX_ERROR
from utils.utils import g_vscode_headers_instance, get_copilot_token


def select_token(ip: str, token_pool: list) -> str:
    # 将IP地址转换为整数
    ip_int = int(ipaddress.ip_address(ip))

    # 计算哈希值
    hash_obj = hashlib.md5()
    hash_obj.update(str(ip_int).encode())
    hash_value = int(hash_obj.hexdigest(), 16)
    return token_pool[hash_value % len(token_pool)]


def check_remove_token(token: str) -> None:
    if token not in g_token_pool_errors:
        return
    g_token_pool_errors[token] += 1
    if g_token_pool_errors[token] > TOKEN_MAX_ERROR:
        g_token_pool.remove(token)
        del g_token_pool_errors[token]


async def get_tokens(request: Request) -> Tuple[int, str]:
    if IS_SHARE:
        token_pool = g_token_pool.copy()
        while token_pool:
            github_token = select_token(request.client.host, token_pool)
            status_code, copilot_token = await get_copilot_token(github_token, TOKEN_POOL[github_token])
            if status_code == 200:
                return 200, copilot_token.get("token")
            token_pool.remove(github_token)
            check_remove_token(github_token)
        return 401, "all token is invalid"
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
        **g_vscode_headers_instance.base_headers,
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

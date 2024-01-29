#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/11/01 15:00:47
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import hashlib
import random
import time
import uuid
from urllib.parse import urlparse

from config import COPILOT_CHAT_URL, GITHUB_TOKEN_URL, SALT
from utils.cache import get_token_from_cache, set_token_to_cache
from utils.client_manger import client_manager


class VscodeHeaders:
    copilot_host_name = urlparse(COPILOT_CHAT_URL).hostname

    # session id 1-90 分钟更新一次，machine id 保持不变
    # session id 1/8 1-10, 1/4 10-30, 3/8 30-60, 1/4 60-90 更新
    def __init__(self, github_token):
        self.vscode_machine_id = hashlib.sha256(
            (github_token + SALT).encode()
        ).hexdigest()

        self.last_session_id_time = 0
        self.update_session_id_time = self.gen_session_id_update_time()

        self._vscode_session_id = None
        self._vscode_machine_id = None

    @staticmethod
    def gen_session_id_update_time():
        ranges = [(60, 600), (600, 1800), (1800, 3600), (3600, 5400)]
        weights = [1 / 8, 1 / 4, 3 / 8, 1 / 4]
        chose_range = random.choices(ranges, weights=weights)[0]
        return random.randint(*chose_range)

    @property
    def request_id(self) -> str:
        return str(uuid.uuid4())

    @property
    def vscode_session_id(self) -> str:
        now = int(time.time())
        if now - self.last_session_id_time > self.update_session_id_time:
            self.last_session_id_time = now
            self.update_session_id_time = self.gen_session_id_update_time()
            self._vscode_session_id = str(uuid.uuid4()) + str(int(time.time() * 1000))
        return self._vscode_session_id

    @property
    def base_headers(self) -> dict:
        return {
            "Host": self.copilot_host_name,
            "X-Request-Id": self.request_id,
            "Vscode-Sessionid": self.vscode_session_id,
            "Vscode-Machineid": self.vscode_machine_id,
            "X-Github-Api-Version": "2023-07-07",
            "Editor-Version": "vscode/1.85.0",
            "Editor-Plugin-Version": "copilot-chat/0.11.1",
            "Openai-Organization": "github-copilot",
            "Copilot-Integration-Id": "vscode-chat",
            "Openai-Intent": "conversation-panel",
            "Content-Type": "application/json",
            "User-Agent": "GitHubCopilotChat/0.11.1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "connection": "keep-alive",
        }


async def get_copilot_token(github_token, get_token_url=GITHUB_TOKEN_URL):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        token_host_name = urlparse(get_token_url).hostname
        # 请求 github 接口获取 copilot_token
        headers = {
            "Host": token_host_name,
            "Authorization": f"token {github_token}",
            "Editor-Version": "vscode/1.85.0",
            "Editor-Plugin-Version": "copilot-chat/0.11.1",
            "User-Agent": "GitHubCopilotChat/0.11.1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = await client_manager.client.get(get_token_url, headers=headers)
        if response.status_code != 200:
            return response.status_code, response.text
        copilot_token = response.json()
        # 保存到 cache
        set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token


def pares_url_token(url_token: str) -> tuple:
    if "||" not in url_token:
        return GITHUB_TOKEN_URL, url_token
    get_token_url, github_token = url_token.split("||", 1)
    return get_token_url, github_token

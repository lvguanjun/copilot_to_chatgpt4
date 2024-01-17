#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   client_manger.py
@Time    :   2023/11/01 22:31:28
@Author  :   lvguanjun
@Desc    :   client_manger.py
"""


import httpx


class ClientManager:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        return self._client

    def init_client(self):
        # default max_connections=100, max_keepalive_connections=20, keepalive_expiry=5.0, timeout=5.0
        # reference: https://www.python-httpx.org/api/#asyncclient
        self._client = httpx.AsyncClient()

    async def close_client(self):
        if self._client:
            await self._client.aclose()
            self._client = None


client_manager = ClientManager()

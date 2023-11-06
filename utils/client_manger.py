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
        self._client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=10)
        )

    async def close_client(self):
        if self._client:
            await self._client.aclose()
            self._client = None


client_manager = ClientManager()

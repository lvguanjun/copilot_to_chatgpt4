#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   test_copilot_proxy.py
@Time    :   2023/11/06 19:16:19
@Author  :   lvguanjun
@Desc    :   test_copilot_proxy.py
"""

import asyncio
import os
import random

import httpx
import pytest

# 你的接口地址
url = "http://localhost:8080/v1/chat/completions"

# 获取环境变量中的token
token = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"Bearer {token}"}

json_data = {
    "messages": [
        {
            "role": "system",
            "content": 'You are an AI programming assistant.\nWhen asked for your name, you must respond with "GitHub Copilot".\nFollow the user"s requirements carefully & to the letter.',
        },
        {"role": "user", "content": "写一篇800字的关于人工智能的文章。"},
    ],
    "model": "copilot-chat",
    "temperature": 0.1,
    "top_p": 1,
    "n": 1,
    "stream": True,
    "intent": True,
}


# 调用测试函数
@pytest.mark.asyncio
async def test_run():
    max_concurrent_requests = 30  # 设置同时并发数
    total_requests = 50  # 设置最终请求次数
    non_200_responses = 0
    max_non_200_percent = 5

    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def simulate_user_request(client, i):
        nonlocal non_200_responses
        async with semaphore:
            async with client.stream("POST", url, json=json_data) as response:
                if response.status_code != 200:
                    non_200_responses += 1
                await response.aread()

    async def test_stress():
        nonlocal non_200_responses
        async with httpx.AsyncClient(
            headers=headers, timeout=httpx.Timeout(10)
        ) as client:
            tasks = (simulate_user_request(client, i) for i in range(total_requests))
            await asyncio.gather(*tasks)
        non_200_percent = (non_200_responses / total_requests) * 100
        print(f"{non_200_responses=}, {total_requests=}")
        assert non_200_percent <= max_non_200_percent

    await test_stress()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   logger.py
@Time    :   2023/11/01 21:51:04
@Author  :   lvguanjun
@Desc    :   logger.py
"""

from aiologger import Logger, levels
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler

from config import DEBUG, STREAM_LOG

logger = Logger(name="server_logger", level=levels.LogLevel.INFO)
if DEBUG:
    logger.level = levels.LogLevel.DEBUG

logger_format = "%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s"
logger_format = Formatter(fmt=logger_format)

file_handler = AsyncFileHandler(filename="app.log")
file_handler.formatter = logger_format
logger.add_handler(file_handler)

if STREAM_LOG:
    logger.add_handler(AsyncStreamHandler(formatter=logger_format))

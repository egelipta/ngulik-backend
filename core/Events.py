# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: pjvms-backend event monitoring
"""

from typing import Callable
from fastapi import FastAPI
from database.mysql import register_mysql
from database.redis import sys_cache, code_cache
from aioredis import Redis


def startup(app: FastAPI) -> Callable:
    """
    pjvms starting
    :param app: FastAPI
    :return: start_app
    """
    async def app_start() -> None:
        # APP启动完成后触发
        print("pjvms-backend has been started")
        # 注册数据库
        await register_mysql(app)
        # 注入缓存到app state
        app.state.cache = await sys_cache()
        app.state.code_cache = await code_cache()

        pass
    return app_start


def stopping(app: FastAPI) -> Callable:
    """
    pjvms stopping
    :param app: FastAPI
    :return: stop_app
    """
    async def stop_app() -> None:
        # APP停止时触发
        print("pjvms-backend stopping...")
        cache: Redis = await app.state.cache
        code: Redis = await app.state.code_cache
        await cache.close()
        await code.close()

    return stop_app

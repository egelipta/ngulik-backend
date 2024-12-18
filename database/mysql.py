# -*- coding:utf-8 -*-
"""
@Time : 2022/4/24 10:15 AM
@Maintainer: dgos
@Des: mysql database
"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import os


# -----------------------Database configuration-----------------------------------
DB_ORM_CONFIG = {
    "connections": {
        "base": {
            'engine': 'tortoise.backends.mysql',
            "credentials": {
                'host': os.getenv('NGULIK_MYSQL_HOST', 'localhost'),
                'user': os.getenv('NGULIK_MYSQL_USER', 'root'),
                'password': os.getenv('NGULIK_MYSQL_PASSWORD', 'rahasia123'),
                'port': os.getenv('NGULIK_MYSQL_PORT', 3307),
                'database': os.getenv('NGULIK_MYSQL_DATABASE_NAME', 'ngulik_db'),
            }
        }

    },
    "apps": {
        "base": {"models": ["models.base"], "default_connection": "base"},
        "tugas": {"models": ["models.tugas"], "default_connection": "base"},
        "heat_map": {"models": ["models.heat_map"], "default_connection": "base"},
        "rack_server": {"models": ["models.rack_server"], "default_connection": "base"},
        "workfloweditor": {"models": ["models.workfloweditor"], "default_connection": "base"},
        "home_assistant": {"models": ["models.home_assistant"], "default_connection": "base"},
    },
    'use_tz': True,
    'timezone': 'Asia/Jakarta'
}


async def register_mysql(app: FastAPI):
    # Register database
    register_tortoise(
        app,
        config=DB_ORM_CONFIG,
        generate_schemas=False,
        add_exception_handlers=False,
    )

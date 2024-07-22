# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: RackServer Extends
"""

import datetime
from typing import Any, Dict, List, Optional
from core.Response import success, fail, res_antd
from models.rack_server import RackServer
from schemas import rack_server
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F

router = APIRouter(prefix='/rack_server')

@router.get("/data-rack-server", summary="Data Rack Server")
async def data_rack_server():
    data = await RackServer.all()
    return data

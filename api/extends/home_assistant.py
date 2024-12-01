# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: HomeAssistant Extends
"""

import datetime
from typing import Any, Dict, List, Optional
from core.Response import success, fail, res_antd
from models.home_assistant import HomeAssistant
from schemas import home_assistant
from schemas.home_assistant import CreateHomeAssistant, UpdateHomeAssistant
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F
import json

router = APIRouter(prefix='/homeassistant')

@router.get("/get-data", summary="Get All Data")
async def get_all_data():
    data = await HomeAssistant.all().order_by('-create_time')
    return data

@router.post("/add-data", summary="Add Data")
async def home_assistant_add(post: CreateHomeAssistant):
    """
    Tugas Add
    :param post: Create Workflow Editor
    :return:
    """
    create_action = await HomeAssistant.create(**post.dict())
    
    if not create_action:
        return fail(msg=f"Failed {post.id}!")
    
    return success(msg=f"{create_action.id} Berhasil ditambahkan")

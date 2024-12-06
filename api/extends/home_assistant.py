# -*- coding:utf-8 -*-
"""
@Time : 2024/11/28 11:59 PM
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
    data = await HomeAssistant.all().order_by('-update_time')
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


@router.put("/update-data", summary="Update Data",
# dependencies=[Security(check_permissions, scopes=["workfloweditor_update"])]
)
async def home_assistant_update(post: UpdateHomeAssistant):
    """
    Update home_assistant
    :param post:
    :return:
    """
    update_action = await HomeAssistant.get_or_none(pk=post.id)
    if not update_action:
        return fail(msg="Data tidak ada")
    data = post.dict()
    data.pop("id")
    await HomeAssistant.filter(pk=post.id).update(**data)
    return success(msg=f"Data Berhasil diubah!")


@router.delete("/del-data", summary="Delete Data", 
# dependencies=[Security(check_permissions, scopes=["home_assistant_delete"])]
)
async def home_assistant_del(req: Request, id: int):
    """
    HomeAssistant Delete
    :param req:
    :return:
    """
    del_action = await HomeAssistant.filter(pk=id).delete()
    if not del_action:
        return fail(msg=f"Gagal dihapus! {id}!")
    return success(msg="Berhasil dihapus!")

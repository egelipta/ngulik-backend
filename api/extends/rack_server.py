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


@router.post("", summary="Rack Server Add",
# dependencies=[Security(check_permissions, scopes=["tugas_add"])]
)
async def rack_server_add(post: rack_server.CreateRackServer):
    """
    Tugas Add
    :param post: CreateTugas
    :return:
    """
    # Filter Tugass
    # get_name_tugas = await Tugas.get_or_none(name_tugas=post.name_tugas)
    # if get_name_tugas:
    #     return fail(msg=f"Tugas {post.name_tugas} sudah ada!")

    create_rack_server = await RackServer.create(**post.dict())
    if not create_rack_server:
        return fail(msg=f"Failed to create Tugas {post.name}!")
    return success(msg=f"{create_rack_server.name} berhasil disimpan")

@router.get("/data-rack-server", summary="Data Rack Server")
async def data_rack_server():
    data = await RackServer.all()
    return data
